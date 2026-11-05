import unittest
from unittest.mock import patch
from signals.scoring import score_signal


class SignalTests(unittest.TestCase):
    def test_native_failure_preserves_watch_only_signal(self):
        event = {"id": "news", "ticker": "AMD", "title": "News"}
        snapshot = {
            "id": "snapshot",
            "news_event_id": "news",
            "ticker": "AMD",
            "feature_data": {"daily_log_returns": [0.01] * 20},
        }
        with patch(
            "signals.scoring.run_quant", side_effect=ValueError("invalid history")
        ):
            signal = score_signal(event, snapshot)
        self.assertEqual(signal["analysis"]["direction"], "watch")
        self.assertEqual(signal["analysis"]["model_error"], "ValueError")
        self.assertIsNone(signal["probability_profit"])

    def test_baseline_is_attention_not_forecast(self):
        event = {"id": "news", "ticker": "AMD", "title": "AMD reports earnings"}
        snapshot = {
            "id": "snapshot",
            "news_event_id": "news",
            "ticker": "AMD",
            "price": 100,
            "volume": 0,
        }
        signal = score_signal(event, snapshot)
        self.assertEqual(signal["score"], 60)
        self.assertEqual(signal["confidence"], 0.4)
        self.assertIsNone(signal["expected_return"])
        self.assertIsNone(signal["probability_profit"])
        self.assertEqual(signal["analysis"]["direction"], "watch")
        self.assertEqual(signal, score_signal(event, snapshot))

    def test_mismatched_inputs_are_rejected(self):
        event = {"id": "news", "ticker": "AMD", "title": "News"}
        for snapshot in (
            {"news_event_id": "other", "ticker": "AMD"},
            {"news_event_id": "news", "ticker": "NVDA"},
        ):
            with self.assertRaises(ValueError):
                score_signal(event, snapshot)
