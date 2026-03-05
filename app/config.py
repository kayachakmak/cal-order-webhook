from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Google OAuth
    google_client_id: str
    google_client_secret: str

    # Google APIs
    google_sheet_id: str
    google_calendar_id: str

    # App
    webhook_secret: str
    domain: str
    app_url: str  # e.g. https://webhook.yourdomain.com
    token_path: str = "/data/token.json"

    # Google OAuth scopes
    google_scopes: list[str] = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/calendar",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
