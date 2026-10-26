"""Smoke tests to verify application foundation initialization."""

import logging
from app.logging_config import setup_logging
from app.main import main


def test_setup_logging():
    """Verify that logger initializes and sets the expected level."""
    logger = setup_logging("DEBUG")
    assert logger.name == "app"
    assert logger.level == logging.DEBUG


def test_main_startup_and_clean_exit(capsys):
    """Verify that main() initializes foundation and exits cleanly with 0."""
    exit_code = main()
    assert exit_code == 0
