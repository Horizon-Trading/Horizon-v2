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

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # type: ignore[call-arg]
