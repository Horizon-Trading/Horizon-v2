from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from pathlib import Path


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    supabase_url: str
    supabase_secret_key: str
    horizon_api_token: str = ""
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @model_validator(mode="after")
    def production_requires_token(self):
        if self.app_env == "production" and len(self.horizon_api_token) < 32:
            raise ValueError(
                "Production requires HORIZON_API_TOKEN of at least 32 characters"
            )
        return self

    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[1] / ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )


settings = Settings()  # type: ignore[call-arg]
