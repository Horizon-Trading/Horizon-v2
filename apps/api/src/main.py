from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.news import router as news_router
from .routes.signals import router as signals_router
from .routes.portfolio import router as portfolio_router

app = FastAPI(
    title="Horizon API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router)
app.include_router(signals_router)
app.include_router(portfolio_router)


@app.get("/health")
def health():
    return {"status": "ok"}
