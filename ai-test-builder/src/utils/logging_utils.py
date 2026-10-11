from __future__ import annotations

import logging


LOGGER_ROOT_NAME = "ai_test_builder"
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(LOGGER_ROOT_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not any(getattr(handler, "_ai_test_builder_handler", False) for handler in logger.handlers):
        handler = logging.StreamHandler()
        handler._ai_test_builder_handler = True  # type: ignore[attr-defined]
        handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        logger.addHandler(handler)

    logger.propagate = False
    return logger


def get_logger(name: str) -> logging.Logger:
    configure_logging()

    clean_name = (name or "").strip()
    if not clean_name:
        return logging.getLogger(LOGGER_ROOT_NAME)

    if clean_name == LOGGER_ROOT_NAME or clean_name.startswith(f"{LOGGER_ROOT_NAME}."):
        return logging.getLogger(clean_name)

    return logging.getLogger(f"{LOGGER_ROOT_NAME}.{clean_name}")
