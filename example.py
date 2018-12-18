from unittest import TestCase

import requests


class ExampleTests(TestCase):

    def test_that_makes_request(self):
        requests.get('http://example.com')

    def test_with_no_request(self):
        pass
