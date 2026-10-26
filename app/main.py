"""Minimal application startup entry point for Trading Community Platform foundation."""

import sys
from app.config import load_settings_from_env
from app.logging_config import setup_logging


def main() -> int:
    """Initialize application foundation and exit cleanly."""
    settings = load_settings_from_env()
    logger = setup_logging(settings.log_level)

    logger.info("=" * 60)
    logger.info("Trading Community Platform foundation initialized")
    logger.info(f"Environment: {settings.app_env} | Log Level: {settings.log_level}")
    logger.info(f"Market Symbol: {settings.delta_symbol} | Timezone: {settings.timezone}")
    logger.info(
        f"Feature Toggles -> Community Bot: {settings.enable_community_bot} | "
        f"Price Alerts: {settings.enable_price_alerts} | "
        f"Trade Execution: {settings.enable_trade_execution}"
    )
    logger.info("Foundation ready. No background polling or orders active.")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
