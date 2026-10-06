import unittest
from scripts import analyze_review_previews as module


class ProviderFailure(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class RetryTests(unittest.TestCase):
    def test_503_recovers_with_bounded_backoff(self):
        calls, waits = [], []
        def operation():
            calls.append(1)
            if len(calls) < 3:
                raise ProviderFailure(503)
            return 'actual-response'
        fn = getattr(module, 'request_with_retry', None)
        if not callable(fn):
            self.fail('Missing bounded transient request retry')
        self.assertEqual(fn(operation, sleep=waits.append), 'actual-response')
        self.assertEqual(len(calls), 3)
        self.assertEqual(waits, [30, 60])

    def test_permanent_failure_is_not_retried(self):
        calls, waits = [], []
        def operation():
            calls.append(1)
            raise ProviderFailure(401)
        fn = getattr(module, 'request_with_retry', None)
        if not callable(fn):
            self.fail('Missing bounded transient request retry')
        with self.assertRaises(ProviderFailure):
            fn(operation, sleep=waits.append)
        self.assertEqual(len(calls), 1)
        self.assertEqual(waits, [])

    def test_persistent_503_stops_after_four_attempts(self):
        calls, waits = [], []
        def operation():
            calls.append(1)
            raise ProviderFailure(503)
        fn = getattr(module, 'request_with_retry', None)
        if not callable(fn):
            self.fail('Missing bounded transient request retry')
        with self.assertRaises(ProviderFailure):
            fn(operation, sleep=waits.append)
        self.assertEqual(len(calls), 4)
        self.assertEqual(waits, [30, 60, 120])


if __name__ == '__main__':
    unittest.main()
