"""
Configuration du logging pour le package fastapi-acl.

Fournit un logger configuré pour l'ensemble du package.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str = "alak_acl", level: Optional[str] = None) -> logging.Logger:
    """
    Crée et configure un logger pour le package.

    Args:
        name: Nom du logger
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    else:
        logger.setLevel(logging.INFO)

    return logger


# Logger principal du package
logger = get_logger()
