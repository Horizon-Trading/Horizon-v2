import unittest
from unittest.mock import Mock, patch
import httpx
from core.retry import retry_persistence


class RetryTests(unittest.TestCase):
    def test_transient_write_retries_with_bound(self):
        operation = Mock(side_effect=[httpx.ConnectError("offline"), {"id": "saved"}])
        with patch("core.retry.time.sleep") as sleep:
            self.assertEqual(retry_persistence(operation), {"id": "saved"})
            sleep.assert_called_once_with(1)
        operation = Mock(side_effect=httpx.ConnectError("offline"))
        with patch("core.retry.time.sleep"), self.assertRaises(httpx.ConnectError):
            retry_persistence(operation)
        self.assertEqual(operation.call_count, 3)

    def test_bad_input_is_not_retried(self):
        operation = Mock(side_effect=ValueError("bad input"))
        with self.assertRaises(ValueError):
            retry_persistence(operation)
        self.assertEqual(operation.call_count, 1)
