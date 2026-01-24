"""
Repository MySQL pour les rôles.

Réutilise l'implémentation PostgreSQL car les deux utilisent SQLAlchemy.
"""

from typing import Optional, Type

from alak_acl.roles.infrastructure.mappers.role_mapper import RoleMapper
from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel
from alak_acl.roles.infrastructure.repositories.postgresql_repository import PostgreSQLRoleRepository
from alak_acl.shared.database.mysql import MySQLDatabase




class MySQLRoleRepository(PostgreSQLRoleRepository):
    """
    Implémentation du repository des rôles pour MySQL.

    Hérite de PostgreSQLRoleRepository car les deux utilisent SQLAlchemy.
    """

    def __init__(
        self,
        db: MySQLDatabase,
        model_class: Type[SQLRoleModel] = SQLRoleModel,
        mapper: Optional[RoleMapper] = None,
    ):
        """
        Initialise le repository.

        Args:
            db: Instance de MySQLDatabase
            model_class: Classe du modèle rôle
            mapper: Instance du mapper
        """
        super().__init__(db, model_class, mapper)  # type: ignore
