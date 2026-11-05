import httpx
import math
from datetime import datetime, timezone

from config import settings


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

    return {
        "ticker": ticker,
        "price": price,
        "volume": volume,
        # "minute_volume": data.get("minuteBar").get("v"), # TODO
        "relative_volume": None,  # TODO
        "market_cap": None,  # TODO
        "float_shares": None,  # TODO
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
