"""
Module database - Connexions aux bases de données.

Supporte MongoDB, PostgreSQL et MySQL de manière asynchrone.
"""

from alak_acl.shared.database.factory import DatabaseFactory, get_database
from alak_acl.shared.database.base import BaseDatabase
from alak_acl.shared.database.postgresql import Base, PostgreSQLDatabase
from alak_acl.shared.database.mysql import MySQLDatabase
from alak_acl.shared.database.mongodb import MongoDBDatabase

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
