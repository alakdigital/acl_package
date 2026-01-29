"""
Modèles de base de données pour la feature Auth.

Ces modèles peuvent être étendus par le développeur pour ajouter
des colonnes/champs personnalisés.

Les imports sont conditionnels (lazy) pour éviter de charger
les dépendances non installées (SQLAlchemy ou motor/pymongo).
"""


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes pour éviter les dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo)
    if name == "MongoAuthUserModel":
        from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel
        return MongoAuthUserModel
    # Modèles SQL (nécessite SQLAlchemy)
    elif name == "SQLAuthUserModel":
        from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel
        return SQLAuthUserModel
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Modèles de base extensibles
    "SQLAuthUserModel",
    "MongoAuthUserModel",
]
