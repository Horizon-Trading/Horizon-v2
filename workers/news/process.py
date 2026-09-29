from temp import save_event


def process_news(article: dict) -> None:
    events = normalize_article(article)
    for event in events:
        save_event(event)


def normalize_article(article: dict) -> list[dict]:
    symbols = article.get("symbols", [])
    events: list[dict] = []

    for ticker in symbols:
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
