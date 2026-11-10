import unittest
from retry import TemporaryError, fetch_with_retry

class ExistingRetryTests(unittest.TestCase):
    def test_success(self):
        self.assertEqual(fetch_with_retry(lambda: "ok"), "ok")
    def test_transient_failure(self):
        outcomes = iter([TemporaryError("later"), "done"])
        def operation():
            value = next(outcomes)
            if isinstance(value, Exception):
                raise value
            return value
        self.assertEqual(fetch_with_retry(operation, retries=1), "done")
