from decimal import Decimal
from news.repository import supabase
from postgrest.exceptions import APIError

TERMINAL = {"filled", "canceled", "expired", "rejected"}


def reserve_order(signal_id: str, ticker: str, quantity: int | Decimal, reason: str,
                  entry_order_id: str | None = None, attempt: int = 0,
                  limit_price: Decimal | None = None) -> dict | None:
    purpose = "exit" if entry_order_id else "entry"
    client_id = f"hzn-{purpose}-{entry_order_id or signal_id}" + (f"-{attempt}" if entry_order_id else "")
    row = {"signal_id": signal_id, "ticker": ticker, "quantity": str(quantity),
           "purpose": purpose, "side": "sell" if entry_order_id else "buy",
           "entry_order_id": entry_order_id, "reason": reason, "client_order_id": client_id,
           "limit_price": str(limit_price) if limit_price is not None else None}
    try:
        return supabase.table("orders").insert(row).execute().data[0]
    except APIError as exc:
        if exc.code != "23505":
            raise
        existing = supabase.table("orders").select("*").eq("client_order_id", client_id).execute().data
        return existing[0] if existing else None


def apply_broker_order(local: dict, broker: dict) -> None:
    if (broker["client_order_id"] != local["client_order_id"] or broker["symbol"] != local["ticker"]
            or broker["side"] != local["side"]):
        raise ValueError("Broker order does not match local intent")
    quantity = Decimal(str(broker["filled_qty"]))
    price = Decimal(str(broker.get("filled_avg_price") or 0))
    if not quantity.is_finite() or quantity < 0 or not price.is_finite() or (quantity > 0 and price <= 0):
        raise ValueError("Invalid broker fill values")
    supabase.rpc("apply_paper_order_state", {
        "local_order_id": local["id"], "broker_id": broker["id"],
        "broker_status": broker["status"], "cumulative_quantity": broker["filled_qty"],
        "average_price": broker.get("filled_avg_price"), "broker_timestamp": broker["updated_at"],
    }).execute()


def record_error(order_id: str, error: str) -> None:
    supabase.table("orders").update({"error": error}).eq("id", order_id).execute()


def tracked_orders() -> list[dict]:
    # Filled entry orders remain tracked until their exposure is closed.
    return (supabase.table("orders").select("*").eq("exposure_closed", False)
            .order("created_at").limit(500).execute().data)
