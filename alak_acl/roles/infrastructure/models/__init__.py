"""
Modèles de base de données pour la feature Roles.

Les imports sont conditionnels (lazy) pour éviter de charger
les dépendances non installées (SQLAlchemy ou motor/pymongo).
"""

from typing import TYPE_CHECKING

# Type hints pour l'autocomplétion IDE (non exécuté à runtime)
if TYPE_CHECKING:
    from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel as SQLRoleModel
    from alak_acl.roles.infrastructure.models.sql_model import SQLUserRoleModel as SQLUserRoleModel
    from alak_acl.roles.infrastructure.models.sql_model import SQLMembershipModel as SQLMembershipModel
    from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel as MongoRoleModel
    from alak_acl.roles.infrastructure.models.mongo_model import MongoUserRoleModel as MongoUserRoleModel


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes pour éviter les dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo)
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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Modèles SQL
    "SQLRoleModel",
    "SQLUserRoleModel",
    "SQLMembershipModel",
    # Modèles MongoDB
    "MongoRoleModel",
    "MongoUserRoleModel",
]
