"""
Central logging configuration for job-copilot.
All modules get a logger with: logger = get_logger(__name__)
setup_logging() is called at module import time in main.py.
"""
import logging
import sys


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-26s | %(message)s"
DATE_FORMAT = "%H:%M:%S"


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    Configure the root logger. Safe to call multiple times (idempotent).

    IMPORTANT: Uses sys.stderr — uvicorn's reload subprocess passes stderr
    straight through without buffering, so our logs always appear alongside
    uvicorn's own output. Using stdout causes the child process to buffer
    and lose log lines.
    """
    root = logging.getLogger("copilot")
    # Avoid adding duplicate handlers on hot-reload
    if root.handlers:
        return

    # stderr is passed through by uvicorn's reloader without buffering
    handlers = [
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("data/app.log", encoding="utf-8")
    ]
    
    for h in handlers:
        h.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        root.addHandler(h)

    root.setLevel(level)
    root.propagate = False  # don't bubble up to uvicorn's root logger


def get_logger(name: str) -> logging.Logger:
    """
    Returns a child logger under the 'copilot' namespace.
    Usage:  logger = get_logger(__name__)
    """
    short = name.replace("scrapers.", "scraper.").split(".")[-1]
    return logging.getLogger(f"copilot.{short}")
