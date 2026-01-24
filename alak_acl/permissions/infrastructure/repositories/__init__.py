"""
Repositories pour la feature Permissions.
"""

from alak_acl.permissions.infrastructure.repositories.mongodb_repository import MongoDBPermissionRepository
from alak_acl.permissions.infrastructure.repositories.mysql_repository import MySQLPermissionRepository
from alak_acl.permissions.infrastructure.repositories.postgresql_repository import PostgreSQLPermissionRepository


__all__ = [
    "PostgreSQLPermissionRepository",
    "MySQLPermissionRepository",
    "MongoDBPermissionRepository",
]
