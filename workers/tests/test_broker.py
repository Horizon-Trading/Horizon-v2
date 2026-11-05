import unittest
from unittest.mock import patch
import httpx
from trader.broker import paper_base_url, order_by_client_id, submit_order


class BrokerTests(unittest.TestCase):
    def test_live_and_redirect_destinations_are_rejected(self):
        for url in ("https://api.alpaca.markets", "http://paper-api.alpaca.markets", "https://paper-api.alpaca.markets.evil.test", "https://paper-api.alpaca.markets/?key=oops", "https://user@paper-api.alpaca.markets", "https://paper-api.alpaca.markets:8443"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                paper_base_url(url)
        self.assertEqual(paper_base_url("https://paper-api.alpaca.markets/v2/"), "https://paper-api.alpaca.markets/v2")

    def test_ambiguous_submission_reuses_client_id(self):
        intent = {"client_order_id": "hzn-test", "symbol": "AAPL"}
        accepted = {**intent, "id": "broker-order"}
        with patch("trader.broker.order_by_client_id", side_effect=[None, accepted]), \
             patch("trader.broker.request", side_effect=httpx.ReadTimeout("timeout")) as request:
            with self.assertRaises(httpx.ReadTimeout):
                submit_order(intent)
            self.assertEqual(submit_order(intent), accepted)
            self.assertEqual(request.call_count, 1)

    def test_lookup_only_treats_404_as_absence(self):
        for status in (404, 401, 429, 500):
            response = httpx.Response(status, request=httpx.Request("GET", "https://example.invalid"))
            error = httpx.HTTPStatusError("status", request=response.request, response=response)
            with patch("trader.broker.request", side_effect=error):
                if status == 404:
                    self.assertIsNone(order_by_client_id("test"))
                else:
                    with self.assertRaises(httpx.HTTPStatusError):
                        order_by_client_id("test")
