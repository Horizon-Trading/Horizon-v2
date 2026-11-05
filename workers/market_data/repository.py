from typing import Any, cast

from supabase import create_client
from config import settings

supabase = create_client(
    settings.supabase_url,
    settings.supabase_secret_key,
)


def save_snapshot(news_event_id: str, snapshot: dict) -> dict:
    row = {**snapshot, "news_event_id": news_event_id}
    # A replay or two competing retries must not replace the first observation.
    supabase.table("market_snapshots").upsert(
        row, on_conflict="news_event_id", ignore_duplicates=True,
    ).execute()
    saved = get_snapshot(news_event_id)
    if saved is None:
        raise RuntimeError("Snapshot write returned no persisted row")
    return saved


def get_snapshot(news_event_id: str) -> dict | None:
    response = supabase.table("market_snapshots").select("*").eq("news_event_id", news_event_id).limit(1).execute()
    return cast(dict[str, Any], response.data[0]) if response.data else None
