"""Explicitly enrich stored observations; never fetch or fabricate historical news."""
import argparse
import logging
from datetime import datetime

from news.analysis import classify_event, summarize
from news.repository import supabase
from market_data.features import get_features
from market_data.repository import get_snapshot
from signals.scoring import score_signal
from signals.repository import save_signal


def reanalyze(limit: int = 20) -> int:
    events = (supabase.table("news_events").select("*").eq("provider", "alpaca")
              .order("received_at", desc=True).limit(limit).execute().data)
    updated = 0
    for event in events:
        try:
            snapshot = get_snapshot(event["id"])
            if not snapshot:
                continue
            enrichment = {"event_type": classify_event(event["title"]),
                          "summary": summarize({"summary": event.get("summary"), "headline": event["title"]})}
            supabase.table("news_events").update(enrichment).eq("id", event["id"]).execute()
            event.update(enrichment)
            features = get_features(event["ticker"], datetime.fromisoformat(snapshot["captured_at"]))
            supabase.table("market_snapshots").update(features).eq("id", snapshot["id"]).execute()
            snapshot.update(features)
            save_signal(score_signal(event, snapshot))
            updated += 1
        except Exception as exc:
            logging.getLogger(__name__).warning("Reanalysis failed ticker=%s error=%s", event["ticker"], type(exc).__name__)
    return updated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("limit must be between 1 and 100")
    print(f"Updated {reanalyze(args.limit)} stored observations")
