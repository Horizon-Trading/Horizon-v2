import unittest
from news.analysis import classify_event, summarize


class NewsAnalysisTests(unittest.TestCase):
    def test_summary_uses_provider_and_strips_markup(self):
        self.assertEqual(summarize({"summary": "<p>A &amp; B</p><script>secret()</script>", "content": "fallback"}), "A & B")

    def test_summary_falls_back_and_is_bounded(self):
        self.assertEqual(summarize({"summary": None, "content": "<p>Body</p>"}), "Body")
        self.assertEqual(summarize({"headline": "Headline"}), "Headline")
        self.assertLessEqual(len(summarize({"content": "word " * 200})), 400)

    def test_classification_is_explicit_and_has_unknown_fallback(self):
        self.assertEqual(classify_event("Company reports quarterly earnings"), "earnings")
        self.assertEqual(classify_event("Company announces partnership"), "partnership")
        self.assertEqual(classify_event("Markets open higher"), "other")
