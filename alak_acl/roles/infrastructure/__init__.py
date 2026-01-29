"""
Couche infrastructure de la feature Roles.

Les imports sont conditionnels pour éviter de charger des dépendances
non installées (SQLAlchemy ou motor/pymongo).
"""

from alak_acl.roles.infrastructure.mappers.role_mapper import RoleMapper


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes pour éviter les dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo/bson)
    if name == "MongoRoleModel":
        from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel
        return MongoRoleModel
    elif name == "MongoUserRoleModel":
        from alak_acl.roles.infrastructure.models.mongo_model import MongoUserRoleModel
        return MongoUserRoleModel
    # Modèles SQL (nécessite SQLAlchemy)
    elif name == "SQLRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel
        return SQLRoleModel
    elif name == "SQLUserRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLUserRoleModel
        return SQLUserRoleModel
    elif name == "SQLMembershipModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLMembershipModel
        return SQLMembershipModel
    # Repositories
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
    # Modèles SQL
    "SQLRoleModel",
    "SQLUserRoleModel",
    "SQLMembershipModel",
    # Modèles MongoDB
    "MongoRoleModel",
    "MongoUserRoleModel",
    # Mapper
    "RoleMapper",
]
