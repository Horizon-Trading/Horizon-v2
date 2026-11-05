from datetime import datetime, timezone
from news.repository import supabase


def save_signal(signal: dict) -> dict:
    row = {**signal, "updated_at": datetime.now(timezone.utc).isoformat()}
    response = supabase.table("signals").upsert(row, on_conflict="news_event_id").execute()
    return response.data[0]


def pending_signal_events() -> list[dict]:
    return supabase.rpc("pending_signal_events", {"batch_size": 20}).execute().data
