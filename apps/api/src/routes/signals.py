from fastapi import APIRouter
from ..db import supabase

router = APIRouter(
    prefix="/signals",
    tags=["signals"],
)


@router.get("")
def get_signals():
    response = (
        supabase.table("signals")
        .select("*, news_event:news_events(*), market_snapshot:market_snapshots(*)")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


@router.get("/{signal_id}")
def get_signal(signal_id: str):
    response = (
        supabase.table("signals")
        .select("*, news_event:news_events(*), market_snapshot:market_snapshots(*)")
        .eq("id", signal_id)
        .single()
        .execute()
    )

    return response.data
