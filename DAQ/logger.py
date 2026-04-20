# logger.py
import logging
import os
import random
from datetime import datetime


def setup_logger(log_path):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
fingerprint = '%08x' % random.randrange(16**8)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Log file name
log_filename = f"log_{timestamp}_{fingerprint}.txt"


log_path = os.path.join(LOG_DIR, log_filename)
logger = setup_logger(log_path)
