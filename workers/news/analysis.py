"""Small, transparent news enrichment; provider symbols remain authoritative."""
import re
from html.parser import HTMLParser


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        self.parts.append(" ")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    parser = _TextParser()
    parser.feed(value)
    return " ".join("".join(parser.parts).split())


def summarize(article: dict) -> str:
    for field in ("summary", "content", "headline"):
        text = plain_text(article.get(field))
        if text:
            return text if len(text) <= 400 else text[:397].rsplit(" ", 1)[0] + "..."
    return ""


def classify_event(title: str) -> str:
    # Priority is explicit; these labels describe keywords, not sentiment.
    rules = (
        ("earnings", r"\b(earnings|quarterly results|eps|quarterly revenue)\b"),
        ("merger_acquisition", r"\b(acquires?|acquisition|merger|buyout)\b"),
        ("regulatory", r"\b(fda|regulatory|approval|antitrust|lawsuit)\b"),
        ("financing", r"\b(offering|financing|buyback|dividend)\b"),
        ("analyst_rating", r"\b(upgrades?|downgrades?|price target)\b"),
        ("partnership", r"\b(partnership|partners? with|collaboration)\b"),
        ("product_launch", r"\b(launches?|unveils?|introduces?)\b"),
    )
    for category, pattern in rules:
        if re.search(pattern, title, re.IGNORECASE):
            return category
    return "other"
