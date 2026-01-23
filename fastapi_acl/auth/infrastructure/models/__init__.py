"""
Modèles de base de données pour la feature Auth.
"""

from .sql_model import SQLAuthUserModel
from .mongo_model import MongoAuthUserModel

__all__ = [
    "SQLAuthUserModel",
    "MongoAuthUserModel",
]
