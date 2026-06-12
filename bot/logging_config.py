import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "trading_bot.log"


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure structured logging to both file and console."""
    LOG_DIR.mkdir(exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    root = logging.getLogger("trading_bot")
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.propagate = False

    return root


logger = setup_logging()
