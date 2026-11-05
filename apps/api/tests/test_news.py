import sys
import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.domain import news_with_latency


class NewsTests(unittest.TestCase):
    def test_latency_preserves_clock_skew_and_hides_payload(self):
        row = {"published_at": "2026-11-04T15:00:00Z", "received_at": "2026-11-04T15:00:05Z", "raw_data": {"content": "body"}}
        result = news_with_latency(row)
        self.assertEqual(result["ingestion_latency_seconds"], 5)
        self.assertNotIn("raw_data", result)
        self.assertIn("raw_data", row)
        self.assertIsNone(news_with_latency({})["ingestion_latency_seconds"])
        row["received_at"] = "2026-11-04T14:59:59Z"
        self.assertEqual(news_with_latency(row)["ingestion_latency_seconds"], -1)

    def test_feed_bounds_and_pagination(self):
        db = ModuleType("src.db")
        db.supabase = MagicMock()
        query = db.supabase.table.return_value.select.return_value.order.return_value.order.return_value
        query.range.return_value.execute.return_value.data = [{"id": "test"}]
        with patch.dict(sys.modules, {"src.db": db}):
            from src.routes.news import router
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            response = client.get("/news?limit=10&offset=5")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()[0]["id"], "test")
            query.range.assert_called_once_with(5, 14)
            for path in ("/news?limit=101", "/news?limit=0", "/news?offset=-1"):
                self.assertEqual(client.get(path).status_code, 422)
