"""
Module database - Connexions aux bases de données.

Supporte MongoDB, PostgreSQL et MySQL de manière asynchrone.
"""

from .factory import DatabaseFactory, get_database
from .base import BaseDatabase
from .postgresql import Base, PostgreSQLDatabase
from .mysql import MySQLDatabase
from .mongodb import MongoDBDatabase

__all__ = [
    "DatabaseFactory",
    "get_database",
    "BaseDatabase",
    # Base SQLAlchemy pour les migrations
    "Base",
    # Classes de connexion
    "PostgreSQLDatabase",
    "MySQLDatabase",
    "MongoDBDatabase",
]
