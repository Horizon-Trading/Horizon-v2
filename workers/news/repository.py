from supabase import create_client
from workers.config import settings

supabase = create_client(
    settings.supabase_url,
    settings.supabase_secret_key,
)


def save_event(event: dict) -> None:
    (
        supabase.table("news_events")
        .upsert(
            event,
            on_conflict="provider,provider_event_id,ticker",
        )
        .execute()
    )
