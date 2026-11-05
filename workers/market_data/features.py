"""Completed-session IEX features. Never compare a partial day with full days."""
from datetime import datetime, time, timedelta
from math import isfinite, log, sqrt
from statistics import mean, stdev
from zoneinfo import ZoneInfo

import httpx

NEW_YORK = ZoneInfo("America/New_York")
WINDOW = 20


def historical_bars(ticker: str, captured_at: datetime) -> dict[str, list[dict]]:
    from config import settings

    cutoff = datetime.combine(captured_at.astimezone(NEW_YORK).date(), time.min, NEW_YORK)
    params = {
        "symbols": ",".join(dict.fromkeys([ticker, "SPY"])), "timeframe": "1Day",
        "start": (cutoff - timedelta(days=90)).isoformat(),
        "end": (cutoff - timedelta(microseconds=1)).isoformat(),
        "asof": cutoff.date().isoformat(), "adjustment": "split", "feed": "iex",
        "limit": 1000, "sort": "asc",
    }
    result: dict[str, list[dict]] = {ticker: [], "SPY": []}
    with httpx.Client(timeout=15.0, headers={
        "APCA-API-KEY-ID": settings.alpaca_api_key_id,
        "APCA-API-SECRET-KEY": settings.alpaca_api_secret_key,
    }) as client:
        seen_tokens = set()
        for _ in range(10):
            response = client.get(settings.alpaca_data_url.rstrip("/") + "/stocks/bars", params=params)
            response.raise_for_status()
            payload = response.json()
            bars = payload.get("bars") or {}
            if not isinstance(bars, dict):
                raise ValueError("Invalid historical bars")
            for symbol in result:
                result[symbol].extend(bars.get(symbol) or [])
            token = payload.get("next_page_token")
            if not token:
                return result
            if token in seen_tokens:
                raise ValueError("Repeated history pagination token")
            seen_tokens.add(token)
            params["page_token"] = token
    raise ValueError("Historical bars exceeded bounded page limit")


def clean_bars(bars: list[dict], captured_at: datetime) -> list[dict]:
    cutoff = captured_at.astimezone(NEW_YORK).date()
    by_date = {}
    for bar in bars:
        try:
            observed = datetime.fromisoformat(bar["t"].replace("Z", "+00:00"))
            if observed.tzinfo is None:
                continue
            day = observed.astimezone(NEW_YORK).date()
            close, volume = bar["c"], bar.get("v")
            if day >= cutoff or isinstance(close, bool) or not isinstance(close, (int, float)) or not isfinite(close) or close <= 0:
                continue
            if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not isfinite(volume) or volume < 0:
                volume = None
            by_date[day] = {"date": day.isoformat(), "close": close, "volume": volume}
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    return [by_date[day] for day in sorted(by_date)][-(WINDOW + 1):]


def calculate_features(stock: list[dict], benchmark: list[dict], captured_at: datetime) -> dict:
    bars = clean_bars(stock, captured_at)
    market = {bar["date"]: bar for bar in clean_bars(benchmark, captured_at)}
    returns = [log(current["close"] / previous["close"]) for previous, current in zip(bars, bars[1:])]
    change = adjusted = relative_volume = volatility = None
    # Missing benchmark sessions mean stock bars may span multiple trading days.
    dates = [bar["date"] for bar in bars]
    aligned = len(bars) >= 2 and dates == sorted(market)[-len(bars):]
    if len(bars) >= 2:
        previous, latest = bars[-2:]
        if previous["date"] in market and latest["date"] in market:
            adjacent_market_dates = sorted(market)[-2:]
            if [previous["date"], latest["date"]] == adjacent_market_dates:
                change = latest["close"] / previous["close"] - 1
                adjusted = change - (market[latest["date"]]["close"] / market[previous["date"]]["close"] - 1)
    if aligned and len(returns) == WINDOW:
        volatility = stdev(returns) * sqrt(252)
        volumes = [bar["volume"] for bar in bars[:-1]]
        if all(volume is not None for volume in volumes) and bars[-1]["volume"] is not None:
            baseline = mean(volumes)
            if baseline > 0:
                relative_volume = bars[-1]["volume"] / baseline
    return {
        "price_change": change, "market_adjusted_return": adjusted,
        "relative_volume": relative_volume, "volatility": volatility,
        "feature_data": {
            "status": "complete" if volatility is not None else "insufficient_history",
            "feed": "iex", "adjustment": "split", "benchmark": "SPY", "window": WINDOW,
            "as_of": dates[-1] if dates else None, "bars": bars,
            "benchmark_bars": list(market.values()),
            "daily_log_returns": returns if aligned and len(returns) == WINDOW else [],
            "definitions": "Prior completed NY sessions; close-to-close return; latest full-session volume / prior 20-session mean; stock minus SPY return; sample log-return volatility annualized by sqrt(252).",
        },
    }


def get_features(ticker: str, captured_at: datetime) -> dict:
    history = historical_bars(ticker, captured_at)
    return calculate_features(history[ticker], history["SPY"], captured_at)
