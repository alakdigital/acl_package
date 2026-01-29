"""
Couche infrastructure de la feature Permissions.

Les imports sont conditionnels pour éviter de charger des dépendances
non installées (SQLAlchemy ou motor/pymongo).
"""

from typing import TYPE_CHECKING

# Type hints pour l'autocomplétion IDE (non exécuté à runtime)
if TYPE_CHECKING:
    from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel as SQLPermissionModel
    from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel as MongoPermissionModel
    from alak_acl.permissions.infrastructure.repositories.postgresql_repository import PostgreSQLPermissionRepository as PostgreSQLPermissionRepository
    from alak_acl.permissions.infrastructure.repositories.mysql_repository import MySQLPermissionRepository as MySQLPermissionRepository
    from alak_acl.permissions.infrastructure.repositories.mongodb_repository import MongoDBPermissionRepository as MongoDBPermissionRepository

from alak_acl.permissions.infrastructure.mappers.permission_mapper import PermissionMapper


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes pour éviter les dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo/bson)
    if name == "MongoPermissionModel":
        from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel
        return MongoPermissionModel
    # Modèles SQL (nécessite SQLAlchemy)
    elif name == "SQLPermissionModel":
        from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
        return SQLPermissionModel
    # Repositories
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
