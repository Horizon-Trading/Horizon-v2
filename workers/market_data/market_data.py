import httpx
import math
import logging
from datetime import datetime, timezone

from config import settings
from .features import get_features


def get_latest_quote(ticker: str) -> dict:
    response = httpx.get(settings.alpaca_data_url.rstrip("/") + "/stocks/" + ticker + "/snapshot",
                        headers={"APCA-API-KEY-ID": settings.alpaca_api_key_id,
                                 "APCA-API-SECRET-KEY": settings.alpaca_api_secret_key},
                        params={"feed": "iex"}, timeout=10.0)
    response.raise_for_status()
    trade = response.json().get("latestTrade") or {}
    price = trade.get("p")
    if isinstance(price,bool) or not isinstance(price,(int,float)) or not math.isfinite(price) or price<=0:
        raise ValueError("No valid current trade")
    return {"price": price, "observed_at": trade.get("t")}


def get_market_snapshot(ticker: str) -> dict:
    url = settings.alpaca_data_url + "/stocks/" + ticker + "/snapshot"

    response = httpx.get(
        url,
        headers={
            "APCA-API-KEY-ID": settings.alpaca_api_key_id,
            "APCA-API-SECRET-KEY": settings.alpaca_api_secret_key,
        },
        params={
            "feed": "iex",
        },
        timeout=10.0,
    )

    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Snapshot must be an object")
    trade = data.get("latestTrade") or {}
    bar = data.get("dailyBar") or {}
    price = trade.get("p") if isinstance(trade, dict) else None
    if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
        raise ValueError("Snapshot has no usable latest trade price")
    volume = bar.get("v") if isinstance(bar, dict) else None
    if isinstance(volume, bool) or not isinstance(volume, int) or volume < 0:
        volume = None

    captured_at = datetime.now(timezone.utc)
    features = {"price_change": None, "market_adjusted_return": None, "volatility": None,
                "relative_volume": None, "feature_data": {}}
    try:
        features = get_features(ticker, captured_at)
    except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
        logging.getLogger(__name__).warning("Historical features unavailable ticker=%s error=%s", ticker, type(exc).__name__)
        features["feature_data"] = {"status": "unavailable", "error": type(exc).__name__}

    return {
        "ticker": ticker,
        "price": price,
        "volume": volume,
        "price_observed_at": trade.get("t"),
        "market_cap": None,
        "float_shares": None,
        "captured_at": captured_at.isoformat(),
        **features,
    }
