"""
Module database - Connexions aux bases de données.

Supporte MongoDB, PostgreSQL et MySQL de manière asynchrone.
"""

from .factory import DatabaseFactory, get_database
from .base import BaseDatabase

__all__ = [
    "DatabaseFactory",
    "get_database",
    "BaseDatabase",
]
