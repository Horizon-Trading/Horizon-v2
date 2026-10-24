import httpx
from datetime import datetime, timezone

from workers.config import settings


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
        }
        timeout=10.0,
    )

    response.raise_for_status()
    data=response.json()

    return {
        "ticker": ticker,
        "price": data.get("latestTrade").get("p"),
        "volume": data.get("dailyBar").get("v"),
        "minute_volume": data.get("minuteBar").get("v"),
        "relative_volume": None, # TODO
        "market_cap": None, # TODO
        "float_shares": None, # TODO
        "captured_at": datetime.now(timezone.utc),
    }
