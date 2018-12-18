nose-detecthttp
===============

A nose and pytest plugin that can detect tests making external http calls.
With nose, it adds a single artificial failure with all the results::
    
    $ nosetests -v --with-detecthttp example.py
    test_that_makes_request (example.ExampleTests) ... ok
    test_with_no_request (example.ExampleTests) ... ok

    ======================================================================
    FAIL: Tests made external http calls
    ----------------------------------------------------------------------
    - example.ExampleTests:

        test_that_makes_request:
          GET http://example.com/


    ----------------------------------------------------------------------
    Ran 2 tests in 0.063s

    FAILED (failures=1)

With pytest, failures are added to individual tests::

    $ pytest --with-detecthttp example.py
    ...

    item = <TestCaseFunction 'test_that_makes_request'>

        def pytest_runtest_teardown(item):
            # Note unmocked interactions collected during runtest_call.
            # This is raised here so that pytest doesn't mark it as an internal error.

            report = item.config._detecthttp_reports.pop(item.nodeid, None)
            if item.config._detecthttp_enabled and report:
    >           raise report
    E           UnmockedRequestsDetected: detecthttp noticed the following requests during this test:
    E                 GET http://example.com/

    detecthttp/pytest.py:82: UnmockedRequestsDetected
    ...2 passed, 1 error in 0.35 seconds


Localhost is automatically ignored.
To ignore other hosts, use the `--vcr-ignore-host` option, which takes a comma-delimited list::

    $ nosetests -v --with-detecthttp --vcr-ignore-host=example.com example.py
    test_that_makes_request (example.ExampleTests) ... ok
    test_with_no_request (example.ExampleTests) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.110s

    OK

Under the hood, this wraps every test in a separate `VCR.py cassette <https://github.com/kevin1024/vcrpy>`__.
Since VCR.py's hooks are in the stdlib, this approach won't detect requests made with clients like PycURL.
