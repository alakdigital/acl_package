"""
Repositories - Implémentations concrètes pour chaque DB.
"""

from alak_acl.auth.infrastructure.repositories.mongodb_repository import MongoDBAuthRepository
from alak_acl.auth.infrastructure.repositories.mysql_repository import MySQLAuthRepository
from alak_acl.auth.infrastructure.repositories.postgresql_repository import PostgreSQLAuthRepository


__all__ = [
    "PostgreSQLAuthRepository",
    "MongoDBAuthRepository",
    "MySQLAuthRepository",
]
