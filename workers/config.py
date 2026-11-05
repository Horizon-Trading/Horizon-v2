from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    supabase_url: str
    supabase_secret_key: str

    alpaca_news_url: str
    alpaca_data_url: str
    alpaca_paper_url: str
    alpaca_api_key_id: str
    alpaca_api_secret_key: str
    quant_engine_path: str | None = None
    quant_paths: int = Field(default=10000, ge=1000, le=100000)
    quant_horizon_days: int = Field(default=5, ge=1, le=30)
    paper_trading_enabled: bool = False
    max_order_notional: float = Field(default=100, gt=0, le=10000)
    max_equity_fraction: float = Field(default=.01, gt=0, le=.1)
    max_open_positions: int = Field(default=5, ge=1, le=20)
    min_signal_score: float = Field(default=60, ge=0, le=100)
    min_profit_probability: float = Field(default=.60, ge=.5, le=1)
    max_signal_age_seconds: int = Field(default=900, ge=1, le=3600)
    max_quote_age_seconds: int = Field(default=120, ge=1, le=300)
    min_share_price: float = Field(default=5, gt=0)
    stop_loss_fraction: float = Field(default=.05, gt=0, lt=1)
    take_profit_fraction: float = Field(default=.10, gt=0, le=10)
    max_holding_days: int = Field(default=5, ge=1, le=30)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # type: ignore[call-arg]
