from fastapi import APIRouter, Query
from ..db import supabase
from ..portfolio import performance

router=APIRouter(prefix="/portfolio",tags=["portfolio"])


@router.get("")
def get_portfolio():
    rows=supabase.table("portfolio_snapshots").select("*").order("captured_at",desc=True).limit(1).execute().data
    snapshot=rows[0] if rows else None
    stats=supabase.rpc("portfolio_trade_stats").execute().data
    closed=stats["closed_trades"]
    return {"snapshot":snapshot,"performance":performance(snapshot.get("history") if snapshot else None),
            "closed_trades":closed,"win_rate":stats["winning_trades"]/closed if closed else None,
            "realized_pnl":stats["realized_pnl"],
            "managed_positions":supabase.table("positions").select("*").gt("quantity",0).execute().data}


@router.get("/orders")
def get_orders(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0)):
    return (supabase.table("orders").select("*").order("created_at",desc=True).order("id")
            .range(offset,offset+limit-1).execute().data)


@router.get("/trades")
def get_trades(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0)):
    return (supabase.table("positions").select("*").not_.is_("closed_at","null")
            .order("closed_at",desc=True).order("entry_order_id").range(offset,offset+limit-1).execute().data)
