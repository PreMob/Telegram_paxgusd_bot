"""Tests for application configuration and settings validation."""

import os
from unittest.mock import patch
from app.config import Settings, _get_bool, load_settings_from_env


def test_default_settings():
    """Verify that default settings instantiate with expected baseline values."""
    s = Settings()
    assert s.app_env == "development"
    assert s.log_level == "INFO"
    assert s.timezone == "Asia/Kolkata"
    assert s.delta_symbol == "PAXGUSD"
    assert s.database_url == "sqlite:///./tradebot.db"
    assert s.enable_community_bot is False
    assert s.enable_price_alerts is False
    assert s.enable_trade_execution is False
    assert s.is_development is True
    assert s.is_production is False


def test_settings_validation_fallback():
    """Verify that invalid app_env and log_level fall back to safe defaults."""
    s = Settings(app_env="invalid_env", log_level="unknown_level")
    assert s.app_env == "development"
    assert s.log_level == "INFO"


def test_secrets_masked_in_repr():
    """Ensure sensitive credentials are never displayed in raw text representation."""
    s = Settings(telegram_bot_token="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ")
    repr_str = repr(s)
    assert "ABCdefGHIjklMNOpqrSTUvwxYZ" not in repr_str
    assert "..." in repr_str


def test_get_bool_helper():
    """Test environment variable boolean parser with various truthy/falsy representations."""
    with patch.dict(os.environ, {"TEST_TRUE_1": "1", "TEST_TRUE_2": "true", "TEST_FALSE": "0", "TEST_OFF": "no"}):
        assert _get_bool("TEST_TRUE_1") is True
        assert _get_bool("TEST_TRUE_2") is True
        assert _get_bool("TEST_FALSE") is False
        assert _get_bool("TEST_OFF") is False
        assert _get_bool("NON_EXISTENT", default=True) is True
        assert _get_bool("NON_EXISTENT", default=False) is False


def test_load_settings_from_clean_env():
    """Verify that load_settings_from_env succeeds without needing real secrets."""
    clean_env = {
        "APP_ENV": "testing",
        "LOG_LEVEL": "DEBUG",
        "TIMEZONE": "UTC",
        "DELTA_SYMBOL": "PAXGUSD",
        "ENABLE_COMMUNITY_BOT": "false",
        "ENABLE_PRICE_ALERTS": "false",
        "ENABLE_TRADE_EXECUTION": "false",
    }
    with patch.dict(os.environ, clean_env, clear=True):
        loaded = load_settings_from_env()
        assert loaded.app_env == "testing"
        assert loaded.log_level == "DEBUG"
        assert loaded.timezone == "UTC"
        assert loaded.is_testing is True
        assert loaded.telegram_bot_token is None
