"""
Repository MySQL pour les rôles.

Réutilise l'implémentation PostgreSQL car les deux utilisent SQLAlchemy.
"""

from typing import Optional, Type

from ....shared.database.mysql import MySQLDatabase
from ..models.sql_model import SQLRoleModel
from ..mappers.role_mapper import RoleMapper
from .postgresql_repository import PostgreSQLRoleRepository


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
