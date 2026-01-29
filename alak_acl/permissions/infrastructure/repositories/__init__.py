"""
Repositories pour la feature Permissions.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from typing import TYPE_CHECKING

# Type hints pour l'autocomplétion IDE (non exécuté à runtime)
if TYPE_CHECKING:
    from alak_acl.permissions.infrastructure.repositories.postgresql_repository import PostgreSQLPermissionRepository as PostgreSQLPermissionRepository
    from alak_acl.permissions.infrastructure.repositories.mysql_repository import MySQLPermissionRepository as MySQLPermissionRepository
    from alak_acl.permissions.infrastructure.repositories.mongodb_repository import MongoDBPermissionRepository as MongoDBPermissionRepository


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des repositories pour éviter les dépendances manquantes."""
    if name == "PostgreSQLPermissionRepository":
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
    "PostgreSQLPermissionRepository",
    "MySQLPermissionRepository",
    "MongoDBPermissionRepository",
]
