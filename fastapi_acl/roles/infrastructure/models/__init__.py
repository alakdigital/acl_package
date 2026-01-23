"""
Modèles de base de données pour la feature Roles.
"""

from .sql_model import SQLRoleModel, SQLUserRoleModel, create_role_model, user_roles_table
from .mongo_model import MongoRoleModel, MongoUserRoleModel, create_mongo_role_model

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
