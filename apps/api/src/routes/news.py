from fastapi import APIRouter
from ..db import supabase

router = APIRouter(
    prefix="/news",
    tags=["news"],
)


@router.get("")
def get_news():
    response = supabase.table("news_events").select("*").execute()
    return response.data
