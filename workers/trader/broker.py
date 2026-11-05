"""Alpaca paper-only transport. Credentials can never be sent to a live host."""
from urllib.parse import urlsplit
import httpx


def paper_base_url(value: str) -> str:
    url = urlsplit(value)
    if (url.scheme != "https" or url.hostname != "paper-api.alpaca.markets"
            or url.port not in (None, 443) or url.username or url.password or url.query or url.fragment
            or url.path.rstrip("/") not in ("", "/v2")):
        raise ValueError("Only https://paper-api.alpaca.markets is allowed for trading")
    return "https://paper-api.alpaca.markets/v2"


def request(method: str, path: str, *, params: dict | None = None, body: dict | None = None):
    from config import settings
    base = paper_base_url(settings.alpaca_paper_url)
    if not path.startswith("/") or "://" in path:
        raise ValueError("Invalid broker path")
    response = httpx.request(method, base + path, params=params, json=body, timeout=15.0,
                            follow_redirects=False, headers={
                                "APCA-API-KEY-ID": settings.alpaca_api_key_id,
                                "APCA-API-SECRET-KEY": settings.alpaca_api_secret_key,
                            })
    response.raise_for_status()
    return response.json() if response.content else None


def order_by_client_id(client_order_id: str) -> dict | None:
    try:
        return request("GET", "/orders:by_client_order_id", params={"client_order_id": client_order_id})
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return None
        raise


def submit_order(order: dict) -> dict:
    existing = order_by_client_id(order["client_order_id"])
    if existing:
        return existing
    # Never blindly retry a POST; the next cycle first looks up this same ID.
    return request("POST", "/orders", body=order)
