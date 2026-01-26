"""
Couche infrastructure de la feature Roles.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from alak_acl.roles.infrastructure.mappers.role_mapper import RoleMapper
from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel, MongoUserRoleModel


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes SQL pour éviter les dépendances manquantes."""
    if name == "SQLRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel
        return SQLRoleModel
    elif name == "SQLUserRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLUserRoleModel
        return SQLUserRoleModel
    elif name == "PostgreSQLRoleRepository":
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
    # Repositories
    "PostgreSQLRoleRepository",
    "MySQLRoleRepository",
    "MongoDBRoleRepository",
    # Modèles
    "SQLRoleModel",
    "SQLUserRoleModel",
    "MongoRoleModel",
    "MongoUserRoleModel",
    # Mapper
    "RoleMapper",
]
