from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from secrets import compare_digest
from .config import settings
from .db import supabase
from postgrest.exceptions import APIError
import httpx
import logging
import re

from .routes.news import router as news_router
from .routes.signals import router as signals_router
from .routes.portfolio import router as portfolio_router

app = FastAPI(
    title="Horizon API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router)
app.include_router(signals_router)
app.include_router(portfolio_router)


@app.middleware("http")
async def authenticate(request: Request, call_next):
    if request.url.path != "/health" and settings.horizon_api_token:
        if not compare_digest(
            request.headers.get("x-horizon-token", ""), settings.horizon_api_token
        ):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)


async def dependency_error(request: Request, exc: Exception):
    # Log diagnostic codes only, never provider messages, URLs or credentials.
    code = str(getattr(exc, "code", ""))
    code = code if re.fullmatch(r"[A-Za-z0-9_]{1,32}", code) else "unknown"
    response = getattr(exc, "response", None)
    logging.getLogger(__name__).warning(
        "Dependency failure error=%s code=%s http_status=%s",
        type(exc).__name__, code, getattr(response, "status_code", "unknown"),
    )
    return JSONResponse(status_code=503, content={"detail": "Data service unavailable"})


app.add_exception_handler(APIError, dependency_error)
app.add_exception_handler(httpx.HTTPError, dependency_error)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    supabase.table("signals").select("id").limit(1).execute()
    return {"status": "ready"}


@app.get("/status")
def status():
    return {"workers": supabase.table("worker_status").select("*").execute().data}
