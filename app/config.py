"""Application configuration and environment settings."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root if present
_ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT_DIR / ".env")


def _get_bool(key: str, default: bool = False) -> bool:
    """Safely parse boolean environment variable."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "t", "yes", "y", "on")


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment."""

    app_env: str = "development"
    log_level: str = "INFO"
    timezone: str = "Asia/Kolkata"

    # Telegram Bot Settings (Optional at foundation stage)
    telegram_bot_token: Optional[str] = None
    telegram_channel_id: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    # Delta Exchange Market Data Settings
    delta_base_url: str = "https://api.india.delta.exchange/v2"
    delta_symbol: str = "PAXGUSD"

    # Database Persistence Settings
    database_url: str = "sqlite:///./tradebot.db"

    # Feature Toggles (Safely disabled by default)
    enable_community_bot: bool = False
    enable_price_alerts: bool = False
    enable_trade_execution: bool = False

    def __post_init__(self):
        """Validate settings after initialization."""
        valid_envs = ("development", "staging", "production", "testing")
        if self.app_env.lower() not in valid_envs:
            object.__setattr__(self, "app_env", "development")

        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if self.log_level.upper() not in valid_levels:
            object.__setattr__(self, "log_level", "INFO")

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    @property
    def is_testing(self) -> bool:
        return self.app_env.lower() == "testing"

    def __repr__(self) -> str:
        """Safe string representation masking secret credentials."""
        masked_token = (
            f"{self.telegram_bot_token[:6]}...{self.telegram_bot_token[-4:]}"
            if self.telegram_bot_token and len(self.telegram_bot_token) > 10
            else ("***" if self.telegram_bot_token else "None")
        )
        return (
            f"Settings(app_env={self.app_env!r}, log_level={self.log_level!r}, "
            f"timezone={self.timezone!r}, telegram_bot_token={masked_token!r}, "
            f"telegram_channel_id={self.telegram_channel_id!r}, "
            f"delta_base_url={self.delta_base_url!r}, delta_symbol={self.delta_symbol!r}, "
            f"database_url={self.database_url!r}, "
            f"enable_community_bot={self.enable_community_bot}, "
            f"enable_price_alerts={self.enable_price_alerts}, "
            f"enable_trade_execution={self.enable_trade_execution})"
        )


def load_settings_from_env() -> Settings:
    """Build a Settings instance from current environment variables."""
    # Support backward-compatibility with DELTA_TICKER_URL if present
    delta_url = os.getenv("DELTA_BASE_URL")
    if not delta_url:
        legacy_ticker = os.getenv("DELTA_TICKER_URL", "")
        if legacy_ticker and "publicapi.deltaexchange.io" not in legacy_ticker:
            delta_url = legacy_ticker.rstrip("/").removesuffix("/tickers")
        else:
            delta_url = "https://api.india.delta.exchange/v2"

    return Settings(
        app_env=os.getenv("APP_ENV", "development").strip(),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        timezone=os.getenv("TIMEZONE", "Asia/Kolkata").strip(),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
        telegram_channel_id=os.getenv("TELEGRAM_CHANNEL_ID") or None,
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
        delta_base_url=delta_url.strip(),
        delta_symbol=os.getenv("DELTA_SYMBOL", "PAXGUSD").strip().upper(),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./tradebot.db").strip(),
        enable_community_bot=_get_bool("ENABLE_COMMUNITY_BOT", default=False),
        enable_price_alerts=_get_bool("ENABLE_PRICE_ALERTS", default=False),
        enable_trade_execution=_get_bool("ENABLE_TRADE_EXECUTION", default=False),
    )


# Global singleton settings instance
settings = load_settings_from_env()
