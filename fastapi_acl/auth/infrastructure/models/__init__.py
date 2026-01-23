"""
Modèles de base de données pour la feature Auth.

Ces modèles peuvent être étendus par le développeur pour ajouter
des colonnes/champs personnalisés.
"""

from .sql_model import SQLAuthUserModel, create_user_model
from .mongo_model import MongoAuthUserModel, create_mongo_user_model

__all__ = [
    # Modèles de base extensibles
    "SQLAuthUserModel",
    "MongoAuthUserModel",
    # Factory functions pour créer des modèles dynamiquement
    "create_user_model",
    "create_mongo_user_model",
]
