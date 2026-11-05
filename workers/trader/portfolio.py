from datetime import datetime, timezone
from decimal import Decimal
import logging
from config import settings
from news.repository import supabase
from .broker import request


def capture_portfolio() -> None:
    latest=supabase.table("portfolio_snapshots").select("captured_at").order("captured_at",desc=True).limit(1).execute().data
    if latest and (datetime.now(timezone.utc)-datetime.fromisoformat(latest[0]["captured_at"])).total_seconds()<60:
        return
    account=request("GET","/account")
    positions=request("GET","/positions")
    values={key:Decimal(str(account[key])) for key in ("equity","cash","buying_power")}
    if any(not value.is_finite() for value in values.values()):
        raise ValueError("Nonfinite broker account value")
    row={key:str(value) for key,value in values.items()}
    row["trading_enabled"]=settings.paper_trading_enabled
    fields=("symbol","qty","avg_entry_price","current_price","market_value","unrealized_pl")
    row["broker_positions"]=[{key:position.get(key) for key in fields} for position in positions]
    try:
        row["history"]=request("GET","/account/portfolio/history",params={"period":"1M","timeframe":"1D","cashflow_types":"ALL"})
    except Exception as exc:
        row["history_error"]=type(exc).__name__
        logging.getLogger(__name__).warning("Portfolio history unavailable error=%s",type(exc).__name__)
    supabase.table("portfolio_snapshots").insert(row).execute()
