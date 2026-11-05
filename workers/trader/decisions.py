from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_DOWN
import math


def age_seconds(value: str | None, now: datetime) -> float | None:
    try:
        age = (now - datetime.fromisoformat(value.replace("Z", "+00:00"))).total_seconds()
        return age if age >= 0 else None
    except (ValueError, TypeError, AttributeError):
        return None


def qualifies(signal: dict, now: datetime, settings) -> bool:
    event = signal.get("news_event") or {}
    snapshot = signal.get("market_snapshot") or {}
    age = age_seconds(event.get("published_at"), now)
    quote_age = age_seconds(snapshot.get("price_observed_at"), now)
    if (event.get("provider") != "alpaca" or event.get("source") == "test"
            or signal.get("model_version") != "normal-log-returns-v1"
            or (signal.get("analysis") or {}).get("direction") != "long"
            or age is None or age > settings.max_signal_age_seconds
            or quote_age is None or quote_age > settings.max_quote_age_seconds):
        return False
    for key in ("score", "probability_profit", "expected_return"):
        value = signal.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return False
    return (signal["score"] >= settings.min_signal_score
            and settings.min_profit_probability <= signal["probability_profit"] <= 1
            and signal["expected_return"] > 0)


def order_quantity(account: dict, price: float, settings) -> int:
    if account.get("status") != "ACTIVE" or account.get("trading_blocked") or account.get("account_blocked"):
        return 0
    try:
        equity, cash, buying_power, quote = (Decimal(str(value)) for value in
            (account.get("equity"), account.get("cash"), account.get("buying_power"), price))
        if any(not value.is_finite() or value <= 0 for value in (equity, cash, buying_power, quote)) or quote < Decimal(str(settings.min_share_price)):
            return 0
        budget = min(Decimal(str(settings.max_order_notional)), equity * Decimal(str(settings.max_equity_fraction)), cash, buying_power)
        # Leave a 1% cash buffer for movement between decision and market fill.
        return int((budget / (quote * Decimal("1.01"))).to_integral_value(rounding=ROUND_DOWN))
    except (InvalidOperation, TypeError, ValueError):
        return 0


def exit_reason(position: dict, price: float, now: datetime, settings) -> str | None:
    held = age_seconds(position.get("opened_at"), now)
    if held is not None and held >= settings.max_holding_days * 86400:
        return "max_holding_period"
    basis = float(position["avg_entry_price"])
    if not math.isfinite(price) or price <= 0 or not math.isfinite(basis) or basis <= 0:
        return None
    change = price / basis - 1
    if change <= -settings.stop_loss_fraction:
        return "stop_loss"
    if change >= settings.take_profit_fraction:
        return "take_profit"
    return None
