"""Настройки из переменных окружения."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


def _env_int(key: str) -> int | None:
    raw = os.getenv(key)
    if raw is None or not str(raw).strip():
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        return None


def sqlite_path_from_database_url(url: str) -> Path:
    """Парсит sqlite:///leads.db или sqlite:///C:/path/leads.db."""
    prefix = "sqlite:///"
    if not url.strip().lower().startswith("sqlite:///"):
        raise ValueError("DATABASE_URL должен начинаться с sqlite:///")
    rest = url.strip()[len(prefix) :].strip()
    if not rest:
        rest = "leads.db"
    return Path(rest)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_chat_id: int | None
    contact_text: str
    database_path: Path
    log_level: str

    @classmethod
    def from_env(cls) -> Settings:
        db_url = _env("DATABASE_URL", "sqlite:///leads.db")
        return cls(
            bot_token=_env("BOT_TOKEN"),
            admin_chat_id=_env_int("ADMIN_CHAT_ID"),
            contact_text=_env(
                "CONTACT_TEXT",
                "Свяжитесь с нами удобным способом из описания бота.",
            ),
            database_path=sqlite_path_from_database_url(db_url),
            log_level=_env("LOG_LEVEL", "INFO").upper() or "INFO",
        )


def get_settings() -> Settings:
    return Settings.from_env()
