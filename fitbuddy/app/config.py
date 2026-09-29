from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "FitBuddy"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./data/fitbuddy.db")
    )
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    workout_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.8-flash")
    )
    tip_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_TIP_MODEL", "gemini-3.5-flash-lite")
    )
    admin_token: str = Field(default_factory=lambda: os.getenv("ADMIN_TOKEN", "change-this-admin-token"))

    @property
    def ai_enabled(self) -> bool:
        return bool(self.gemini_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
