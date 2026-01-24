"""
Modèles de persistance pour la feature Permissions.
"""

from .sql_model import SQLPermissionModel
from .mongo_model import MongoPermissionModel

__all__ = [
    "SQLPermissionModel",
    "MongoPermissionModel",
]
