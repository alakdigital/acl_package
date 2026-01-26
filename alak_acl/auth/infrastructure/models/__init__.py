"""
Modèles de base de données pour la feature Auth.

Ces modèles peuvent être étendus par le développeur pour ajouter
des colonnes/champs personnalisés.

Les imports SQL sont conditionnels pour éviter de charger SQLAlchemy
si l'utilisateur n'utilise que MongoDB.
"""

from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel, create_mongo_user_model


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes SQL pour éviter les dépendances manquantes."""
    if name == "SQLAuthUserModel":
        from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel
        return SQLAuthUserModel
    elif name == "create_user_model":
        from alak_acl.auth.infrastructure.models.sql_model import create_user_model
        return create_user_model
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Modèles de base extensibles
    "SQLAuthUserModel",
    "MongoAuthUserModel",
    # Factory functions pour créer des modèles dynamiquement
    "create_user_model",
    "create_mongo_user_model",
]
