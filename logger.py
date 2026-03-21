import logging
import os

def setup_logger(log_path: str) -> logging.Logger:
    """Sets up and returns a logger that writes to a log file."""
    logger = logging.getLogger("file_organizer")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
