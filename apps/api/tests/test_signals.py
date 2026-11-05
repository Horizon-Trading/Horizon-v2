import importlib
import sys
import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient


class SignalApiTests(unittest.TestCase):
    def setUp(self):
        db = ModuleType("src.db")
        db.supabase = MagicMock()
        with patch.dict(sys.modules, {"src.db": db}):
            self.routes = importlib.import_module("src.routes.signals")
        self.mock = patch.object(self.routes, "supabase", db.supabase)
        self.mock.start()
        self.addCleanup(self.mock.stop)
        self.db = db.supabase
        app = FastAPI()
        app.include_router(self.routes.router)
        self.client = TestClient(app)

    def test_invalid_and_missing_signal(self):
        self.assertEqual(self.client.get("/signals/bad-id").status_code, 422)
        self.db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
        self.assertEqual(self.client.get("/signals/11111111-1111-1111-1111-111111111111").status_code, 404)

    def test_joined_signal_and_feed_bounds(self):
        query = self.db.table.return_value.select.return_value.order.return_value.order.return_value
        query.range.return_value.execute.return_value.data = [{"id": "signal", "news_event": {"raw_data": {"body": "large"}}}]
        response = self.client.get("/signals?limit=2&offset=4")
        self.assertEqual(response.status_code, 200)
        query.range.assert_called_once_with(4, 5)
        self.assertNotIn("raw_data", response.json()[0]["news_event"])
        self.assertEqual(self.client.get("/signals?limit=101").status_code, 422)
