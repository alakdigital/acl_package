"""
Repositories - Implémentations concrètes pour chaque DB.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from typing import TYPE_CHECKING

# Type hints pour l'autocomplétion IDE (non exécuté à runtime)
if TYPE_CHECKING:
    from alak_acl.auth.infrastructure.repositories.postgresql_repository import PostgreSQLAuthRepository as PostgreSQLAuthRepository
    from alak_acl.auth.infrastructure.repositories.mysql_repository import MySQLAuthRepository as MySQLAuthRepository
    from alak_acl.auth.infrastructure.repositories.mongodb_repository import MongoDBAuthRepository as MongoDBAuthRepository


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des repositories pour éviter les dépendances manquantes."""
    if name == "PostgreSQLAuthRepository":
        from alak_acl.auth.infrastructure.repositories.postgresql_repository import PostgreSQLAuthRepository
        return PostgreSQLAuthRepository
    elif name == "MySQLAuthRepository":
        from alak_acl.auth.infrastructure.repositories.mysql_repository import MySQLAuthRepository
        return MySQLAuthRepository
    elif name == "MongoDBAuthRepository":
        from alak_acl.auth.infrastructure.repositories.mongodb_repository import MongoDBAuthRepository
        return MongoDBAuthRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "PostgreSQLAuthRepository",
    "MongoDBAuthRepository",
    "MySQLAuthRepository",
]
