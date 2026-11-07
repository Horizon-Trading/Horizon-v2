import os
import unittest
from unittest.mock import patch

from config import Settings


class ConfigTests(unittest.TestCase):
    def test_deployment_needs_credentials_but_not_provider_url_overrides(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(
                _env_file=None,
                supabase_url="https://example.supabase.co",
                supabase_secret_key="test-secret",
                alpaca_api_key_id="test-key",
                alpaca_api_secret_key="test-secret",
            )
        self.assertEqual(settings.alpaca_news_url, "wss://stream.data.alpaca.markets/v1beta1/news")
        self.assertEqual(settings.alpaca_data_url, "https://data.alpaca.markets/v2")
        self.assertEqual(settings.alpaca_paper_url, "https://paper-api.alpaca.markets/v2")
        self.assertFalse(settings.paper_trading_enabled)
