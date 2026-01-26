"""
Modèles de base de données pour la feature Roles.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel, MongoUserRoleModel, create_mongo_role_model


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes SQL pour éviter les dépendances manquantes."""
    if name == "SQLRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel
        return SQLRoleModel
    elif name == "SQLUserRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLUserRoleModel
        return SQLUserRoleModel
    elif name == "create_role_model":
        from alak_acl.roles.infrastructure.models.sql_model import create_role_model
        return create_role_model
    elif name == "user_roles_table":
        from alak_acl.roles.infrastructure.models.sql_model import user_roles_table
        return user_roles_table
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Modèles SQL
    "SQLRoleModel",
    "SQLUserRoleModel",
    "create_role_model",
    "user_roles_table",
    # Modèles MongoDB
    "MongoRoleModel",
    "MongoUserRoleModel",
    "create_mongo_role_model",
]
