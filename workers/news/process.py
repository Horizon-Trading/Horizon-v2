import logging
import re
from datetime import datetime

from .repository import save_event
from market_data.market_data import get_market_snapshot
from market_data.repository import save_snapshot

logger = logging.getLogger(__name__)


def process_news(article: dict) -> None:
    try:
        events = normalize_article(article)
    except (ValueError, TypeError, KeyError):
        logger.warning("Skipping malformed news article")
        return

    for event in events:
        try:
            saved_event = save_event(event)
            snapshot = get_market_snapshot(saved_event["ticker"])
            save_snapshot(saved_event["id"], snapshot)
        except Exception as exc:
            # A provider/persistence failure must not discard other symbols.
            # Do not log response bodies, raw articles or credentials.
            logger.error(
                "News processing failed provider_event_id=%s ticker=%s error=%s",
                event["provider_event_id"], event["ticker"], type(exc).__name__,
            )


def normalize_article(article: dict) -> list[dict]:
    if not isinstance(article, dict):
        raise ValueError("Article must be an object")
    for field in ("headline", "url", "created_at"):
        if not isinstance(article.get(field), str) or not article[field].strip():
            raise ValueError(f"Missing {field}")
    if isinstance(article.get("id"), bool) or not isinstance(article.get("id"), (str, int)):
        raise ValueError("Missing provider ID")
    if not str(article["id"]).strip():
        raise ValueError("Empty provider ID")
    published_at = datetime.fromisoformat(article["created_at"].replace("Z", "+00:00"))
    if published_at.tzinfo is None:
        raise ValueError("Publication timestamp must include timezone")
    symbols = article.get("symbols", [])
    if not isinstance(symbols, list):
        raise ValueError("Symbols must be an array")
    events: list[dict] = []
    seen: set[str] = set()

    for ticker in symbols:
        if not isinstance(ticker, str):
            continue
        ticker = ticker.strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,14}", ticker) or ticker in seen:
            continue
        seen.add(ticker)
        events.append(
            {
                "provider": "alpaca",
                "provider_event_id": str(article["id"]),
                "ticker": ticker,
                "title": article["headline"],
                "summary": article.get("summary"),
                "url": article["url"],
                "source": article.get("source"),
                "author": article.get("author"),
                "published_at": article["created_at"],
                "raw_data": article,
            }
        )

    return events
