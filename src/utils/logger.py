"""Logging utility for the SEO blog generator."""

import logging
import sys
from typing import Optional

from src.config import get_config


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger.

    Args:
        name: Logger name
        level: Optional log level override

    Returns:
        Configured logger
    """
    # Get log level from config if not specified
    if level is None:
        level = get_config().logging.log_level

    # Create logger
    logger = logging.getLogger(name)

    # Set level
    level_obj = getattr(logging, level.upper())
    logger.setLevel(level_obj)

    # Only add handlers if they don't exist
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level_obj)

        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger
