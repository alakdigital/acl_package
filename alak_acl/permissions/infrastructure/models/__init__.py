"""
Modèles de persistance pour la feature Permissions.

Les imports sont conditionnels (lazy) pour éviter de charger
les dépendances non installées (SQLAlchemy ou motor/pymongo).
"""


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes pour éviter les dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo)
    if name == "MongoPermissionModel":
        from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel
        return MongoPermissionModel
    # Modèles SQL (nécessite SQLAlchemy)
    elif name == "SQLPermissionModel":
        from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
        return SQLPermissionModel
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "SQLPermissionModel",
    "MongoPermissionModel",
]
