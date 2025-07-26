# src/logger/__init__.py

import logging
import os
from datetime import datetime
from from_root import from_root

# Create a single log file path at import time
LOG_FILE = os.path.join(
    from_root(), "logs", f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
