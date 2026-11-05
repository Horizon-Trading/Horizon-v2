from typing import Any, cast
from datetime import datetime, timedelta, timezone

from supabase import create_client
from config import settings

supabase = create_client(
    settings.supabase_url,
    settings.supabase_secret_key,
)


def save_event(event: dict) -> dict:
    response = (
        supabase.table("news_events")
        .upsert(
            event,
            on_conflict="provider,provider_event_id,ticker",
        )
        .execute()
    )

    return cast(dict[str, Any], response.data[0])


def record_snapshot_attempt(event: dict, error: str | None = None) -> None:
    attempts = event.get("snapshot_attempts", 0) + 1
    supabase.table("news_events").update({
        "snapshot_attempts": attempts,
        "next_snapshot_attempt_at": (datetime.now(timezone.utc) + timedelta(seconds=min(30 * 2 ** min(attempts - 1, 6), 1800))).isoformat(),
        "snapshot_error": error,
    }).eq("id", event["id"]).execute()


def pending_snapshot_events() -> list[dict]:
    return cast(list[dict], supabase.rpc("pending_snapshot_events", {"batch_size": 20}).execute().data)
