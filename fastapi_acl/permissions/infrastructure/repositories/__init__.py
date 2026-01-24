"""
Repositories pour la feature Permissions.
"""

from .postgresql_repository import PostgreSQLPermissionRepository
from .mysql_repository import MySQLPermissionRepository
from .mongodb_repository import MongoDBPermissionRepository

__all__ = [
    "PostgreSQLPermissionRepository",
    "MySQLPermissionRepository",
    "MongoDBPermissionRepository",
]
