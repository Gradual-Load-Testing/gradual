import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger():
    log_dir = Path("logs")
    Path.mkdir(log_dir, exist_ok=True, parents=True)

    logger = logging.getLogger("api_logger")
    logger.setLevel(logging.INFO)

    log_file = log_dir / "api_requests.log"

    # Rotate every 5 MB, keep last 5 log files
    handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger
