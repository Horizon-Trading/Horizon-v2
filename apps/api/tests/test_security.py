import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class SecurityTests(unittest.TestCase):
    def test_token_required_except_liveness(self):
        config = ModuleType("src.config")
        config.settings = SimpleNamespace(
            cors_origins=[], horizon_api_token="test-token"
        )
        db = ModuleType("src.db")
        db.supabase = MagicMock()
        with patch.dict(sys.modules, {"src.config": config, "src.db": db}):
            from src import main
        with (
            patch.object(main, "settings", config.settings),
            patch.object(main, "supabase", db.supabase),
        ):
            client = TestClient(main.app)
            self.assertEqual(client.get("/health").status_code, 200)
            self.assertEqual(client.get("/ready").status_code, 401)
            self.assertEqual(
                client.get("/ready", headers={"x-horizon-token": "wrong"}).status_code,
                401,
            )
            self.assertEqual(
                client.get(
                    "/ready", headers={"x-horizon-token": "test-token"}
                ).status_code,
                200,
            )
