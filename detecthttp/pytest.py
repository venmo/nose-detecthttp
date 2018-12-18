from __future__ import absolute_import

import sys

import pytest
import vcr


class UnmockedRequestsDetected(Exception):
    def __init__(self, cassette):
        self.cassette = cassette

    def __str__(self):
        output = []
        output.append('detecthttp noticed the following requests during this test:')
        for request in self.cassette.requests:
            output.append("      %s %s" % (request.method, request.url.split('?')[0]))

        return '\n'.join(output)


def pytest_addoption(parser):
    group = parser.getgroup('detecthttp', 'detect external http requests')

    group.addoption(
        '--with-detecthttp', action='store_true',
        default=False, dest="detecthttp",
        help="Enable detecthttp.")

    group.addoption(
        '--no-detecthttp', action='store_true',
        default=False, dest="nodetecthttp",
        help="Disable detecthttp. Has the most precedence.")

    group.addoption(
        '--vcr-ignore-host', action='store',
        default='', dest='ignored_hosts',
        help="Ignore external calls to certain hosts. Accepts a comma-separated list.")


def pytest_configure(config):
    config._detecthttp_enabled = False
    if config.getoption('detecthttp') and not config.getoption('nodetecthttp'):
        config._detecthttp_enabled = True

    config._detecthttp_ignored_hosts = filter(bool, config.getoption('ignored_hosts').split(','))
    config._detecthttp_reports = {}  # nodeid -> UnmockedReport


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    enabled = item.config._detecthttp_enabled
    if enabled:
        cassette_name = "%s.yaml" % item
        cassette_manager = vcr.use_cassette(
            cassette_name,
            serializer='yaml',
            record_mode='once',
            ignore_localhost=True,
            ignore_hosts=item.config._detecthttp_ignored_hosts)

        cassette = cassette_manager.__enter__()
        assert not cassette.rewound  # this cassette shouldn't be from disk

        # Prevent the cassette from being written out.
        cassette._save = lambda *args, **kwargs: None

    yield

    if enabled:
        cassette_manager.__exit__(*sys.exc_info())
        if len(cassette):
            error_report = UnmockedRequestsDetected(cassette)
            item.config._detecthttp_reports[item.nodeid] = error_report


def pytest_runtest_teardown(item):
    # Note unmocked interactions collected during runtest_call.
    # This is raised here so that pytest doesn't mark it as an internal error.

    report = item.config._detecthttp_reports.pop(item.nodeid, None)
    if item.config._detecthttp_enabled and report:
        raise report
