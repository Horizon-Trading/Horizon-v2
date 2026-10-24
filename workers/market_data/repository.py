from typing import Any, cast

from supabase import create_client
from config import settings

supabase = create_client(
    settings.supabase_url,
    settings.supabase_secret_key,
)


def save_snapshot(news_event_id: str, snapshot: dict) -> dict:
    row = {"news_event_id": news_event_id, **snapshot}
    response = supabase.table("market_snapshots").insert(row).execute()
    return cast(dict[str, Any], response.data[0])
