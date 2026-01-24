"""
Modèles de base de données pour la feature Roles.
"""

from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel, MongoUserRoleModel, create_mongo_role_model
from alak_acl.roles.infrastructure.models.sql_model import (
    SQLRoleModel, SQLUserRoleModel, 
    create_role_model, 
    user_roles_table
)


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
