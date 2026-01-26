"""
Couche infrastructure de la feature Permissions.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from alak_acl.permissions.infrastructure.mappers.permission_mapper import PermissionMapper
from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes SQL pour éviter les dépendances manquantes."""
    if name == "SQLPermissionModel":
        from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
        return SQLPermissionModel
    elif name == "PostgreSQLPermissionRepository":
        from alak_acl.permissions.infrastructure.repositories.postgresql_repository import PostgreSQLPermissionRepository
        return PostgreSQLPermissionRepository
    elif name == "MySQLPermissionRepository":
        from alak_acl.permissions.infrastructure.repositories.mysql_repository import MySQLPermissionRepository
        return MySQLPermissionRepository
    elif name == "MongoDBPermissionRepository":
        from alak_acl.permissions.infrastructure.repositories.mongodb_repository import MongoDBPermissionRepository
        return MongoDBPermissionRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Repositories
    "PostgreSQLPermissionRepository",
    "MySQLPermissionRepository",
    "MongoDBPermissionRepository",
    # Modèles
    "SQLPermissionModel",
    "MongoPermissionModel",
    # Mapper
    "PermissionMapper",
]
