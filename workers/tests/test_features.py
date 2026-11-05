import math
import sys
import unittest
from datetime import datetime, timedelta, timezone
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch
from market_data.features import calculate_features, historical_bars


class FeatureTests(unittest.TestCase):
    def bars(self, growth=1.01):
        return [{"t": (datetime(2026, 9, 1, 4, tzinfo=timezone.utc) + timedelta(days=i)).isoformat(),
                 "c": 100 * growth ** i, "v": 200 if i == 20 else 100} for i in range(21)]

    def test_known_returns_volume_and_volatility(self):
        captured = datetime(2026, 9, 22, 15, tzinfo=timezone.utc)
        result = calculate_features(self.bars(), self.bars(1.005), captured)
        self.assertAlmostEqual(result["price_change"], .01)
        self.assertAlmostEqual(result["market_adjusted_return"], .005)
        self.assertEqual(result["relative_volume"], 2)
        self.assertAlmostEqual(result["volatility"], 0, places=12)
        self.assertEqual(len(result["feature_data"]["daily_log_returns"]), 20)

    def test_partial_day_and_future_bars_are_excluded(self):
        bars = self.bars() + [{"t": "2026-09-22T04:00:00Z", "c": 9999, "v": 999999}]
        result = calculate_features(bars, bars, datetime(2026, 9, 22, 15, tzinfo=timezone.utc))
        self.assertEqual(result["feature_data"]["as_of"], "2026-09-21")
        self.assertEqual(result["relative_volume"], 2)

    def test_missing_sessions_or_zero_baseline_are_not_fabricated(self):
        stock, market = self.bars(), self.bars()
        del stock[10]
        result = calculate_features(stock, market, datetime(2026, 9, 22, tzinfo=timezone.utc))
        self.assertIsNone(result["volatility"])
        self.assertEqual(result["feature_data"]["daily_log_returns"], [])
        stock = self.bars()
        for bar in stock:
            bar["v"] = 0
        result = calculate_features(stock, market, datetime(2026, 9, 22, 15, tzinfo=timezone.utc))
        self.assertIsNone(result["relative_volume"])

    def test_invalid_bars_and_empty_history(self):
        result = calculate_features([{"t": "bad", "c": math.nan}], [], datetime.now(timezone.utc))
        self.assertIsNone(result["price_change"])
        self.assertIsNone(result["volatility"])

    def test_historical_pagination_keeps_both_symbols(self):
        config = ModuleType("config")
        config.settings = SimpleNamespace(alpaca_api_key_id="test", alpaca_api_secret_key="test", alpaca_data_url="https://example.invalid/v2")
        first, second = MagicMock(), MagicMock()
        first.json.return_value = {"bars": {"AAPL": self.bars()}, "next_page_token": "next"}
        second.json.return_value = {"bars": {"SPY": self.bars()}, "next_page_token": None}
        with patch.dict(sys.modules, {"config": config}), patch("market_data.features.httpx.Client") as client:
            client.return_value.__enter__.return_value.get.side_effect = [first, second]
            result = historical_bars("AAPL", datetime(2026, 9, 22, 15, tzinfo=timezone.utc))
            self.assertEqual(len(result["AAPL"]), 21)
            self.assertEqual(len(result["SPY"]), 21)
            self.assertEqual(client.return_value.__enter__.return_value.get.call_count, 2)
