"""
src/utils/logging.py
--------------------
Lightweight structured logging for the review engine.
Wraps Python's standard logging with a consistent format.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger with a consistent format.

    Usage:
        from src.utils.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Ingested 42 reviews from Play Store")
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger
