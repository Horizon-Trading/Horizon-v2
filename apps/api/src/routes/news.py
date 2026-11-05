from fastapi import APIRouter, Query
from ..db import supabase
from ..domain import news_with_latency

router = APIRouter(
    prefix="/news",
    tags=["news"],
)


@router.get("")
def get_news(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    response = (supabase.table("news_events").select("*")
                .order("published_at", desc=True).order("id")
                .range(offset, offset + limit - 1).execute())
    return [news_with_latency(row) for row in response.data]
