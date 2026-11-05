import logging
from . import broker
from .repository import TERMINAL, apply_broker_order, record_error, tracked_orders

logger = logging.getLogger(__name__)


def reconcile_orders() -> None:
    for local in tracked_orders():
        if local["purpose"] == "exit" and local["status"] in TERMINAL:
            continue
        try:
            remote = broker.order_by_client_id(local["client_order_id"])
            if remote is not None:
                apply_broker_order(local, remote)
        except Exception as exc:
            record_error(local["id"], type(exc).__name__)
            logger.warning("Order reconciliation failed order_id=%s error=%s", local["id"], type(exc).__name__)


def send_reserved_order(local: dict) -> None:
    if local["status"] != "pending_submit":
        return
    payload = {"client_order_id": local["client_order_id"], "symbol": local["ticker"],
               "qty": str(local["quantity"]), "side": local["side"], "type": "market",
               "time_in_force": "day"}
    try:
        remote = broker.submit_order(payload)
        apply_broker_order(local, remote)
    except Exception as exc:
        # Preserve the intent on ambiguous network/HTTP failures. Future cycles
        # look up the same ID before considering resubmission.
        record_error(local["id"], type(exc).__name__)
        logger.warning("Order submission unresolved order_id=%s error=%s", local["id"], type(exc).__name__)
