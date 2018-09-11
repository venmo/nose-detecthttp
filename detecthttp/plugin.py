from collections import defaultdict
from functools import partial
from operator import itemgetter
import sys

from nose.case import Test
from nose.plugins import Plugin
from nose.plugins.xunit import Xunit as XunitPlugin
import vcr


class VcrFailuresTest(object):
    # This is just a callable with custom __str__, since
    # apparently overriding __str__ on lambdas doesn't do anything.
    def __str__(self):
        return "Tests made external http calls"

    def __call__(self):
        pass

    id = __str__


class UnmockedReport(Exception):
    # We need to defer generation of this output to when all tests are done.
    # Because there's no nose hook after tests but before report output,
    # we use this object to encapsulate it.
    def __init__(self):
        self.unmocked_tests = defaultdict(partial(defaultdict, list))
        # {'my.module.MyClass': {'my_test': cassette}}

    def add(self, test, cassette):
        raw = repr(test)  # 'Test(<my.module testMethod=test_save_me_user>)'
        raw = raw[6:-2]
        module_and_class, next_el = raw.split(' ')[:2]

        test_name = next_el.split('=')[-1]

        self.unmocked_tests[module_and_class][test_name] = cassette

    def __str__(self):
        output = []
        for module_and_class, failures in sorted(self.unmocked_tests.iteritems(),
                                                 key=itemgetter(0)):
            output.append("- %s:" % module_and_class)
            output.append('')
            for test_name, cassette in failures.items():
                output.append("    %s:" % test_name)
                for request in cassette.requests:
                    output.append("      %s %s" % (request.method, request.url.split('?')[0]))
                output.append('')
            output.append('')

        return '\n'.join(output)


class DetectHTTP(Plugin):
    """
    Detect tests that make http requests.
    Details of detected requests are exposed as a failure also available to xunit.
    """

    name = 'detecthttp'
    score = 3000  # must be higher than 2000 to send results to xunit

    def options(self, parser, env):
        super(DetectHTTP, self).options(parser, env)

        parser.add_option(
            '--no-detecthttp', action='store_true',
            default=False, dest="nodetecthttp",
            help="Disable detecthttp. Has the most precedence.")

        parser.add_option(
            '--vcr-ignore-host', action='store',
            default='', dest='ignored_hosts',
            help="Ignore external calls to certain hosts. Accepts a comma-separated list.")

    def configure(self, options, conf):
        super(DetectHTTP, self).configure(options, conf)

        if options.nodetecthttp:
            self.enabled = False

        self.ignored_hosts = filter(bool, options.ignored_hosts.split(','))

        self.added_failure = False
        self.unmocked_report = UnmockedReport()

    def prepareTestResult(self, result):
        # We need access to the result in stopTest, but it's not usually available.
        self.result = result

    def startTest(self, test):
        """Run this test inside a cassette."""

        cassette_name = "%s.yaml" % test
        self._cassette_manager = vcr.use_cassette(cassette_name,
                                                  serializer='yaml',
                                                  record_mode='once',
                                                  ignore_localhost=True,
                                                  ignore_hosts=self.ignored_hosts)

        self._cassette = self._cassette_manager.__enter__()
        assert not self._cassette.rewound  # this cassette shouldn't be from disk

        # Prevent the cassette from being written out.
        self._cassette._save = lambda *args, **kwargs: None

    def stopTest(self, test):
        """Exit the cassette and note any unmocked interactions."""

        self._cassette_manager.__exit__(*sys.exc_info())
        if len(self._cassette):
            self.unmocked_report.add(test, self._cassette)

            if not self.added_failure:
                test = Test(VcrFailuresTest())
                result = self.unmocked_report
                self.result.failures.append((test, result))
                self.added_failure = True

    def report(self, result):
        if not self.added_failure:
            return

        xunit_plugin = [p for p in self.conf.plugins.plugins if isinstance(p, XunitPlugin)]
        if xunit_plugin:
            xunit_plugin = xunit_plugin[0]
            xunit_plugin.stats['failures'] += 1
            xunit_plugin.errorlist.append(
                '<testcase classname=%(cls)s name=%(name)s time="%(taken).3f">'
                '<failure type=%(errtype)s message=%(message)s><![CDATA[%(tb)s]]>'
                '</failure></testcase>' %
                {'cls': xunit_plugin._quoteattr('DetectHTTPFailure.External_calls_exist'),
                 'name': xunit_plugin._quoteattr('see_message_for_details'),
                 'taken': 0,
                 'errtype': xunit_plugin._quoteattr('DetectHTTPFailure'),
                 'message': xunit_plugin._quoteattr(str(self.unmocked_report)),
                 'tb': xunit_plugin._quoteattr('N/A'),
                 })
