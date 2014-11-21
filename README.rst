nose-detecthttp
===============

A nose plugin that can detect tests making external http calls.
Example output::
    
    $ nosetests -v myapp/
    test_that_makes_request ... ok
    test_with_no_request ... ok

    ======================================================================
    FAIL: Tests made external http calls (--no-detect-http to disable)
    ----------------------------------------------------------------------
    - myapp.tests.AppTest:

        test_that_makes_request:
          GET http://example.com

    ----------------------------------------------------------------------
    Ran 2 tests in 0.001s

    FAILED (failures=1)

Under the hood, this wraps every test in a separate `VCR.py cassette <https://github.com/kevin1024/vcrpy>`__.
Since VCR.py's hooks are in the stdlib, this approach won't detect requests made with clients like PycURL.
