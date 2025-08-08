import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BACKUP_COUNT = 15
FILE_SIZE = 5 * 1024 * 1024


def size_based_logger(
    name: str,
    file_size: int = FILE_SIZE,
    backup_count: int = BACKUP_COUNT,
    log_dir: str = "logs/stress_test",
):
    """
    Create a logger that logs to a file.

    Args:
        name: The name of the logger.
        file_size: The size of the log file in bytes.
        backup_count: The number of backup log files to keep.
        log_dir: The directory to log to.
    """
    log_dir_path = Path(log_dir)
    Path.mkdir(log_dir_path, exist_ok=True, parents=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_file = log_dir_path / f"{name}.log"

    # Rotate every 5 MB, keep last 5 log files
    handler = RotatingFileHandler(
        log_file, maxBytes=file_size, backupCount=backup_count, encoding="utf-8"
    )

    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d]  %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
