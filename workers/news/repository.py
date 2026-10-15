from supabase import create_client
import os
from pathlib import Path
from dotenv import load_dotenv
from process import process_news

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SECRET_KEY = os.environ["SUPABASE_SECRET_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
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
