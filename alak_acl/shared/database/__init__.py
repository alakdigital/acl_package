"""
Module database - Connexions aux bases de données.

Supporte MongoDB, PostgreSQL et MySQL de manière asynchrone.

Les imports sont conditionnels pour éviter de charger des dépendances
non installées (ex: SQLAlchemy pour les utilisateurs MongoDB uniquement).
"""

from typing import TYPE_CHECKING

# Type hints pour l'autocomplétion IDE (non exécuté à runtime)
if TYPE_CHECKING:
    from alak_acl.shared.database.declarative_base import Base as Base
    from alak_acl.shared.database.postgresql import PostgreSQLDatabase as PostgreSQLDatabase
    from alak_acl.shared.database.mysql import MySQLDatabase as MySQLDatabase
    from alak_acl.shared.database.mongodb import MongoDBDatabase as MongoDBDatabase

from alak_acl.shared.database.factory import DatabaseFactory, get_database
from alak_acl.shared.database.base import BaseDatabase

# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes de base de données."""
    if name == "Base":
        from alak_acl.shared.database.declarative_base import Base
        return Base
    elif name == "PostgreSQLDatabase":
        from alak_acl.shared.database.postgresql import PostgreSQLDatabase
        return PostgreSQLDatabase
    elif name == "MySQLDatabase":
        from alak_acl.shared.database.mysql import MySQLDatabase
        return MySQLDatabase
    elif name == "MongoDBDatabase":
        from alak_acl.shared.database.mongodb import MongoDBDatabase
        return MongoDBDatabase
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DatabaseFactory",
    "get_database",
    "BaseDatabase",
    # Base SQLAlchemy pour les migrations (lazy)
    "Base",
    # Classes de connexion (lazy)
    "PostgreSQLDatabase",
    "MySQLDatabase",
    "MongoDBDatabase",
]
