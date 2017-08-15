nose-detecthttp
===============

A nose plugin that can detect tests making external http calls.
Example output::
    
    $ nosetests -v --with-detecthttp myapp/
    test_that_makes_request ... ok
    test_with_no_request ... ok

    ======================================================================
    FAIL: Tests made external http calls
    ----------------------------------------------------------------------
    - myapp.tests.AppTest:

        test_that_makes_request:
          GET http://example.com

    ----------------------------------------------------------------------
    Ran 2 tests in 0.001s

    FAILED (failures=1)

Sometimes, you want to ignore hosts besides localhost. For example, you might
be running tests in a containerized environment where dynamodb has the hostname
`dynamodb` and `mysql` has the hostname `mysql`. To ignore these hosts,
the `--vcr-ignore-host` option::

    nosetests -v --with-detecthttp --vcr-ignore-host=www.example.com app/
    test_one (app.tests.ExternalTestCase) ... ok
    test_two (app.tests.ExternalTestCase) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.042s

    OK

Under the hood, this wraps every test in a separate `VCR.py cassette <https://github.com/kevin1024/vcrpy>`__.
Since VCR.py's hooks are in the stdlib, this approach won't detect requests made with clients like PycURL.
