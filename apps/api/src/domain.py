from datetime import datetime


def news_with_latency(row: dict) -> dict:
    """Signed latency exposes clock skew instead of silently replacing it."""
    result = dict(row)
    try:
        received = datetime.fromisoformat(row["received_at"].replace("Z", "+00:00"))
        published = datetime.fromisoformat(row["published_at"].replace("Z", "+00:00"))
        result["ingestion_latency_seconds"] = (received - published).total_seconds()
    except (KeyError, ValueError, TypeError, AttributeError):
        result["ingestion_latency_seconds"] = None
    # Original provider payload stays in storage, not in public feed responses.
    result.pop("raw_data", None)
    return result
