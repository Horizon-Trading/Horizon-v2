from datetime import datetime, timedelta, timezone
import logging
from news.repository import supabase
from market_data.features import get_features
from signals.scoring import score_signal
from signals.repository import save_signal


def recover_features():
    now = datetime.now(timezone.utc)
    rows = (
        supabase.table("market_snapshots")
        .select("*,news_event:news_events(*)")
        .lt("feature_attempts", 3)
        .lte("next_feature_attempt_at", now.isoformat())
        .order("next_feature_attempt_at")
        .limit(20)
        .execute()
        .data
    )
    for snapshot in rows:
        event = snapshot.get("news_event")
        if not event or event.get("provider") != "alpaca":
            supabase.table("market_snapshots").update({"feature_attempts": 3}).eq(
                "id", snapshot["id"]
            ).execute()
            continue
        attempts = snapshot["feature_attempts"] + 1
        supabase.table("market_snapshots").update(
            {
                "feature_attempts": attempts,
                "next_feature_attempt_at": (
                    now + timedelta(minutes=5 * attempts)
                ).isoformat(),
            }
        ).eq("id", snapshot["id"]).execute()
        try:
            features = snapshot.get("feature_data") or {}
            if features.get("status") not in ("complete", "insufficient_history"):
                calculated = get_features(
                    snapshot["ticker"], datetime.fromisoformat(snapshot["captured_at"])
                )
                snapshot.update(calculated)
                supabase.table("market_snapshots").update(calculated).eq(
                    "id", snapshot["id"]
                ).execute()
            save_signal(score_signal(event, snapshot))
            supabase.table("market_snapshots").update({"feature_attempts": 3}).eq(
                "id", snapshot["id"]
            ).execute()
        except Exception as exc:
            logging.getLogger(__name__).warning(
                "Feature recovery failed ticker=%s error=%s",
                snapshot["ticker"],
                type(exc).__name__,
            )
