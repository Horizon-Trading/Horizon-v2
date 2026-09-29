def process_news(article: dict):
    ticker = extract_ticker(article)
    normalized_article = normalize_article(article, ticker)


def extract_ticker(article: dict) -> str:
    return "TEST"


def normalize_article(article: dict, ticker: str) -> dict:
    return {
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
