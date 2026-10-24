# workers/core/test_event.py

from news.process import process_news

fake_article = {
    "T": "n",
    "id": 999999999,
    "headline": "NVIDIA announces new AI infrastructure partnership",
    "summary": "NVIDIA announced a new partnership focused on AI infrastructure.",
    "author": "Test Author",
    "created_at": "2026-10-24T23:00:00Z",
    "updated_at": "2026-10-24T23:00:00Z",
    "url": "https://example.com/fake-news-event",
    "content": "<p>Fake test article.</p>",
    "symbols": ["NVDA", "AMD"],
    "source": "test",
}

process_news(fake_article)
