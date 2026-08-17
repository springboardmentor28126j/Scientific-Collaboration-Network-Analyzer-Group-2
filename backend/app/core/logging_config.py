import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging() -> None:
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "error.log"), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    access_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "access.log"), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))

    error_logger = logging.getLogger("scna.error")
    error_logger.setLevel(logging.ERROR)
    error_logger.addHandler(error_handler)

    access_logger = logging.getLogger("scna.access")
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)