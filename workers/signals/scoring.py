"""Baseline attention score, deliberately not a direction or return forecast."""

from news.analysis import classify_event
from .native import run_quant
import subprocess


def score_signal(event: dict, snapshot: dict) -> dict:
    if (
        snapshot.get("news_event_id") != event["id"]
        or snapshot["ticker"] != event["ticker"]
    ):
        raise ValueError("Signal inputs refer to different events")
    category = event.get("event_type") or classify_event(event["title"])
    weights = {
        "earnings": 60,
        "merger_acquisition": 65,
        "regulatory": 60,
        "financing": 50,
        "analyst_rating": 45,
        "partnership": 45,
        "product_launch": 45,
        "other": 30,
    }
    score = weights.get(category, 30)
    coverage = (
        sum(
            value is not None
            for value in (
                snapshot.get("price"),
                snapshot.get("volume"),
                snapshot.get("relative_volume"),
                snapshot.get("market_cap"),
                snapshot.get("float_shares"),
            )
        )
        / 5
    )
    signal = {
        "news_event_id": event["id"],
        "market_snapshot_id": snapshot["id"],
        "ticker": event["ticker"],
        "score": score,
        "confidence": coverage,
        "expected_return": None,
        "probability_profit": None,
        "model_version": "baseline-v1",
        "analysis": {
            "event_type": category,
            "score_kind": "keyword_attention",
            "confidence_kind": "snapshot_field_coverage",
            "direction": "watch",
            "explanation": "Category-based attention score; no directional prediction or trading eligibility.",
        },
    }
    returns = (snapshot.get("feature_data") or {}).get("daily_log_returns", [])
    if len(returns) >= 20:
        from config import settings

        try:
            model = run_quant(
                returns, settings.quant_paths, settings.quant_horizon_days
            )
        except (ValueError, OSError, subprocess.SubprocessError, KeyError) as exc:
            signal["analysis"]["model_error"] = type(exc).__name__
            return signal
        signal.update(
            {
                "score": round(0.2 * score + 80 * model["probability_profit"], 2),
                "confidence": min(len(returns) / 60, 1),
                "expected_return": model["expected_return"],
                "probability_profit": model["probability_profit"],
                "model_version": "normal-log-returns-v1",
                "analysis": {
                    "event_type": category,
                    "score_kind": "20pct_news_attention_80pct_model_probability",
                    "confidence_kind": "history_count_divided_by_60",
                    "model": model,
                    "direction": "long"
                    if model["expected_return"] > 0
                    and model["probability_profit"] >= 0.55
                    else "watch",
                },
            }
        )
    return signal
