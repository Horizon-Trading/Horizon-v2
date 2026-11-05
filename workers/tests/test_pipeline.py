"""Offline regression tests: never read credentials or contact real services."""
import asyncio
import importlib
import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = ModuleType("config")
        config.settings = SimpleNamespace(
            supabase_url="http://localhost:54321", supabase_secret_key="test",
            alpaca_data_url="https://data.alpaca.markets/v2",
            alpaca_news_url="wss://example.invalid", alpaca_api_key_id="test",
            alpaca_api_secret_key="test", log_level="INFO",
        )
        cls.modules = patch.dict(sys.modules, {"config": config})
        cls.modules.start()
        cls.client = patch("supabase.create_client", return_value=MagicMock())
        cls.client.start()
        cls.process = importlib.import_module("news.process")
        cls.market = importlib.import_module("market_data.market_data")
        cls.stream = importlib.import_module("news.stream")

    @classmethod
    def tearDownClass(cls):
        cls.client.stop()
        cls.modules.stop()

    def article(self, symbols=None):
        return {"id": 42, "headline": "Event", "url": "https://example.com/news",
                "created_at": "2026-11-04T15:00:00Z",
                "symbols": symbols if symbols is not None else ["NVDA", "AMD"]}

    def setUp(self):
        get = patch.object(self.process, "get_snapshot", return_value=None)
        attempt = patch.object(self.process, "record_snapshot_attempt")
        self.get_saved = get.start()
        self.attempt = attempt.start()
        self.addCleanup(get.stop)
        self.addCleanup(attempt.stop)

    def test_repeated_delivery_reuses_original_snapshot(self):
        self.get_saved.return_value = {"id": "original", "price": 12}
        with patch.object(self.process, "get_market_snapshot") as get:
            self.assertEqual(self.process.capture_snapshot({"id": "news"})["id"], "original")
            get.assert_not_called()
            self.attempt.assert_not_called()

    def test_exhausted_and_not_due_retries_do_not_call_provider(self):
        with patch.object(self.process, "get_market_snapshot") as get:
            self.process.capture_snapshot({"id": "a", "snapshot_attempts": 5})
            self.process.capture_snapshot({"id": "b", "next_snapshot_attempt_at": "2099-01-01T00:00:00Z"})
            get.assert_not_called()

    def test_recovery_continues_after_one_failed_event(self):
        with patch.object(self.process, "pending_snapshot_events", return_value=[{"id": "a"}, {"id": "b"}]), \
             patch.object(self.process, "capture_snapshot", side_effect=[RuntimeError(), {}]) as capture:
            self.process.recover_snapshots()
            self.assertEqual(capture.call_count, 2)

    def test_symbols_are_validated_and_deduplicated(self):
        article = self.article(["NVDA", None, "../bad", "AMD", "nvda", "BRK.B"])
        rows = self.process.normalize_article(article)
        self.assertEqual([r["ticker"] for r in rows], ["NVDA", "AMD", "BRK.B"])
        self.assertIs(rows[0]["raw_data"], article)

    def test_bad_article_does_not_persist(self):
        with patch.object(self.process, "save_event") as save:
            for article in (None, {}, self.article("NVDA"), {**self.article(), "id": None}):
                self.process.process_news(article)
            save.assert_not_called()

    def test_failed_ticker_does_not_block_next_and_saved_id_is_used(self):
        with patch.object(self.process, "save_event", side_effect=[RuntimeError("offline"), {"id": "persisted", "ticker": "AMD"}]), \
             patch.object(self.process, "get_market_snapshot", return_value={"price": 123}) as get, \
             patch.object(self.process, "save_snapshot") as save:
            self.process.process_news(self.article())
            get.assert_called_once_with("AMD")
            save.assert_called_once_with("persisted", {"price": 123})

    def test_snapshot_failure_does_not_block_next_ticker(self):
        with patch.object(self.process, "save_event", side_effect=[{"id": "a", "ticker": "NVDA"}, {"id": "b", "ticker": "AMD"}]), \
             patch.object(self.process, "get_market_snapshot", side_effect=[ValueError(), {"price": 123}]), \
             patch.object(self.process, "save_snapshot") as save:
            self.process.process_news(self.article())
            save.assert_called_once_with("b", {"price": 123})

    def snapshot(self, data):
        response = MagicMock()
        response.json.return_value = data
        with patch.object(self.market.httpx, "get", return_value=response):
            return self.market.get_market_snapshot("AMD")

    def test_missing_volume_stays_null(self):
        row = self.snapshot({"latestTrade": {"p": 123.5}, "dailyBar": None})
        self.assertEqual(row["price"], 123.5)
        self.assertIsNone(row["volume"])
        self.assertIsNone(row["relative_volume"])

    def test_zero_volume_is_valid(self):
        self.assertEqual(self.snapshot({"latestTrade": {"p": 1}, "dailyBar": {"v": 0}})["volume"], 0)

    def test_missing_and_nonfinite_prices_are_rejected(self):
        for price in (None, 0, -1, True, "123", float("nan"), float("inf")):
            with self.subTest(price=price), self.assertRaises(ValueError):
                self.snapshot({"latestTrade": {"p": price}})
        with self.assertRaises(ValueError):
            self.snapshot({"latestTrade": None})

    def test_stream_ignores_malformed_frames(self):
        class Socket:
            async def send(self, message):
                pass

            async def recv(self):
                return '[]'

            async def __aiter__(self):
                for frame in ('bad json', '{}', '[null, 4]', '[{"T":"n","id":42}]'):
                    yield frame

        context = MagicMock()
        context.__aenter__.return_value = Socket()

        async def read():
            return [event async for event in self.stream.stream_news()]

        with patch.object(self.stream.websockets, "connect", return_value=context):
            self.assertEqual(asyncio.run(read()), [{"T": "n", "id": 42}])


if __name__ == "__main__":
    unittest.main()
