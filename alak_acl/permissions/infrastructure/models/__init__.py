"""
Modèles de persistance pour la feature Permissions.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes SQL pour éviter les dépendances manquantes."""
    if name == "SQLPermissionModel":
        from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
        return SQLPermissionModel
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "SQLPermissionModel",
    "MongoPermissionModel",
]
