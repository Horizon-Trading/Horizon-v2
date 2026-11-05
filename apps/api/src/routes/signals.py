from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from ..db import supabase
from ..domain import news_with_latency

router = APIRouter(
    prefix="/signals",
    tags=["signals"],
)


@router.get("")
def get_signals(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    response = (
        supabase.table("signals")
        .select("*, news_event:news_events(*), market_snapshot:market_snapshots!signals_market_snapshot_id_fkey(*)")
        .order("created_at", desc=True)
        .order("id")
        .range(offset, offset + limit - 1)
        .execute()
    )

    return [enrich_signal(row) for row in response.data]


@router.get("/{signal_id}")
def get_signal(signal_id: UUID):
    response = (
        supabase.table("signals")
        .select("*, news_event:news_events(*), market_snapshot:market_snapshots!signals_market_snapshot_id_fkey(*)")
        .eq("id", str(signal_id))
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Signal not found")
    return enrich_signal(response.data[0])


@router.get("/{signal_id}/history")
def get_signal_history(signal_id: UUID, limit: int = Query(50, ge=1, le=100)):
    get_signal(signal_id)
    return (supabase.table("signal_history").select("*").eq("signal_id", str(signal_id))
            .order("recorded_at", desc=True).order("id", desc=True).limit(limit).execute().data)


def enrich_signal(row: dict) -> dict:
    result = dict(row)
    if result.get("news_event"):
        result["news_event"] = news_with_latency(result["news_event"])
    return result

