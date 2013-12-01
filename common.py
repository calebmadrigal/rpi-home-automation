# Raspberry Pi Home Security System - common

__author__ = "Caleb Madrigal"

import logging


def setup_logger(name, log_path, log_level=logging.INFO):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.FileHandler(filename=log_path)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger
