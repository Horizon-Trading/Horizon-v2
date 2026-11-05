"""Single-process, long-only paper coordinator with independent risk checks."""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_UP
import logging

from config import settings
from market_data.market_data import get_latest_quote
from . import broker
from .decisions import age_seconds, exit_reason, order_quantity, qualifies
from .reconcile import reconcile_orders, send_reserved_order
from .repository import TERMINAL, reserve_order, supabase
from .portfolio import capture_portfolio

logger = logging.getLogger(__name__)
JOIN = "*,news_event:news_events(*),market_snapshot:market_snapshots!signals_market_snapshot_id_fkey(*)"


def fresh_quote(ticker: str, now: datetime) -> dict | None:
    quote = get_latest_quote(ticker)
    age = age_seconds(quote["observed_at"], datetime.now(timezone.utc))
    return quote if age is not None and age <= settings.max_quote_age_seconds else None


def trading_cycle() -> None:
    reconcile_orders()
    try:
        capture_portfolio()
    except Exception as exc:
        logger.warning("Portfolio capture failed error=%s",type(exc).__name__)
    if not settings.paper_trading_enabled:
        return
    clock = broker.request("GET", "/clock")
    if not clock["is_open"]:
        return
    now = datetime.now(timezone.utc)
    account = broker.request("GET", "/account")
    remote_positions = {row["symbol"]: row for row in broker.request("GET", "/positions")}
    open_orders = broker.request("GET", "/orders", params={"status":"open", "limit":500})
    # Refuse new entries if the bounded broker list may be truncated.
    can_enter = len(open_orders) < 500
    occupied = set(remote_positions) | {row["symbol"] for row in open_orders}
    positions = supabase.table("positions").select("*").gt("quantity",0).execute().data
    for position in positions:
        try:
            ticker = position["ticker"]
            remote = remote_positions.get(ticker)
            if not remote or Decimal(str(remote["qty"])) != Decimal(str(position["quantity"])):
                logger.warning("Position mismatch; automatic exit deferred ticker=%s", ticker)
                can_enter = False
                continue
            exits = supabase.table("orders").select("*").eq("entry_order_id",position["entry_order_id"]).execute().data
            active_exit = next((row for row in exits if row["status"] not in TERMINAL),None)
            if active_exit:
                send_reserved_order(active_exit)
                continue
            quote = fresh_quote(ticker, now)
            reason = exit_reason(position, quote["price"] if quote else float("nan"), now, settings)
            if not reason:
                continue
            entry = supabase.table("orders").select("*").eq("id",position["entry_order_id"]).single().execute().data
            if entry["status"] not in TERMINAL:
                # Wait for confirmed cancellation before selling a partial entry.
                if entry["broker_order_id"]:
                    broker.request("DELETE", "/orders/"+entry["broker_order_id"])
                continue
            intent = reserve_order(entry["signal_id"],ticker,Decimal(str(position["quantity"])),reason,entry["id"],len(exits))
            if intent:
                send_reserved_order(intent)
        except Exception as exc:
            can_enter = False
            logger.warning("Exit processing failed ticker=%s error=%s", position["ticker"],type(exc).__name__)
    if not can_enter:
        return
    intents = (supabase.table("orders").select("*").eq("purpose","entry")
               .eq("exposure_closed",False).execute().data)
    for intent in intents:
        if intent["status"] in TERMINAL or not intent.get("broker_order_id"):
            continue
        original = (supabase.table("signals").select("news_event:news_events(published_at)")
                    .eq("id",intent["signal_id"]).single().execute().data)
        age=age_seconds((original.get("news_event") or {}).get("published_at"),now)
        if age is None or age>settings.max_signal_age_seconds:
            broker.request("DELETE","/orders/"+intent["broker_order_id"])
    occupied.update(row["ticker"] for row in intents)
    cutoff = (now-timedelta(seconds=settings.max_signal_age_seconds)).isoformat()
    signals = (supabase.table("signals").select(JOIN).gte("created_at",cutoff)
               .order("score",desc=True).limit(50).execute().data)
    for signal in signals:
        try:
            if not qualifies(signal,now,settings):
                continue
            ticker = signal["ticker"]
            existing = next((row for row in intents if row["signal_id"]==signal["id"]),None)
            if existing and existing["status"]=="pending_submit":
                # Recheck the current account and quote before retrying an unknown submission.
                quote=fresh_quote(ticker,now)
                if quote and order_quantity(broker.request("GET","/account"),float(existing.get("limit_price") or quote["price"]),settings)>=Decimal(str(existing["quantity"])):
                    send_reserved_order(existing)
                continue
            if ticker in occupied or len(occupied)>=settings.max_open_positions:
                continue
            asset=broker.request("GET","/assets/"+ticker)
            if not asset.get("tradable") or asset.get("status")!="active" or asset.get("class")!="us_equity":
                continue
            quote=fresh_quote(ticker,now)
            if not quote:
                continue
            # Refresh cash/buying power so sequential orders do not reuse a stale budget.
            account=broker.request("GET","/account")
            limit_price=(Decimal(str(quote["price"]))*Decimal("1.01")).quantize(Decimal(".01"),rounding=ROUND_UP)
            quantity=order_quantity(account,float(limit_price),settings)
            if quantity<=0:
                continue
            intent=reserve_order(signal["id"],ticker,quantity,"qualifying_signal",limit_price=limit_price)
            if intent:
                occupied.add(ticker)
                send_reserved_order(intent)
        except Exception as exc:
            logger.warning("Entry processing failed ticker=%s error=%s",signal["ticker"],type(exc).__name__)


async def run_trader():
    while True:
        try:
            await asyncio.to_thread(trading_cycle)
        except Exception as exc:
            logger.error("Trading cycle failed error=%s",type(exc).__name__)
        await asyncio.sleep(30)


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    trading_cycle()
