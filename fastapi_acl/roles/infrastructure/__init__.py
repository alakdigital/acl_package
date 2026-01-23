"""
Couche infrastructure de la feature Roles.
"""

from .repositories.postgresql_repository import PostgreSQLRoleRepository
from .repositories.mysql_repository import MySQLRoleRepository
from .repositories.mongodb_repository import MongoDBRoleRepository
from .models.sql_model import SQLRoleModel, SQLUserRoleModel
from .models.mongo_model import MongoRoleModel, MongoUserRoleModel
from .mappers.role_mapper import RoleMapper

__all__ = [
    # Repositories
    "PostgreSQLRoleRepository",
    "MySQLRoleRepository",
    "MongoDBRoleRepository",
    # Modèles
    "SQLRoleModel",
    "SQLUserRoleModel",
    "MongoRoleModel",
    "MongoUserRoleModel",
    # Mapper
    "RoleMapper",
]
