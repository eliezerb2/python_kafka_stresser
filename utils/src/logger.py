"""
Shared logging util
"""

import logging


def setup_logging(log_level: str):
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    )
