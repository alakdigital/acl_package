"""
Repositories pour la feature Roles.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from typing import TYPE_CHECKING

# Type hints pour l'autocomplétion IDE (non exécuté à runtime)
if TYPE_CHECKING:
    from alak_acl.roles.infrastructure.repositories.postgresql_repository import PostgreSQLRoleRepository as PostgreSQLRoleRepository
    from alak_acl.roles.infrastructure.repositories.mysql_repository import MySQLRoleRepository as MySQLRoleRepository
    from alak_acl.roles.infrastructure.repositories.mongodb_repository import MongoDBRoleRepository as MongoDBRoleRepository


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des repositories pour éviter les dépendances manquantes."""
    if name == "PostgreSQLRoleRepository":
        from alak_acl.roles.infrastructure.repositories.postgresql_repository import PostgreSQLRoleRepository
        return PostgreSQLRoleRepository
    elif name == "MySQLRoleRepository":
        from alak_acl.roles.infrastructure.repositories.mysql_repository import MySQLRoleRepository
        return MySQLRoleRepository
    elif name == "MongoDBRoleRepository":
        from alak_acl.roles.infrastructure.repositories.mongodb_repository import MongoDBRoleRepository
        return MongoDBRoleRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "PostgreSQLRoleRepository",
    "MySQLRoleRepository",
    "MongoDBRoleRepository",
]
