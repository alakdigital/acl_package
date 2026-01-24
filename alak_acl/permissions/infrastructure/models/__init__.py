"""
Modèles de persistance pour la feature Permissions.
"""

from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel
from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel


__all__ = [
    "SQLPermissionModel",
    "MongoPermissionModel",
]
