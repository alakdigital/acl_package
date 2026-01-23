"""
Repository MySQL pour l'authentification.

Réutilise l'implémentation PostgreSQL car les deux utilisent SQLAlchemy.
Supporte les modèles personnalisés avec colonnes supplémentaires.
"""

from typing import Optional, Type

from ....shared.database.mysql import MySQLDatabase
from ..models.sql_model import SQLAuthUserModel
from ..mappers.auth_user_mapper import AuthUserMapper
from .postgresql_repository import PostgreSQLAuthRepository


class MySQLAuthRepository(PostgreSQLAuthRepository):
    """
    Implémentation du repository d'authentification pour MySQL.

    Hérite de PostgreSQLAuthRepository car les deux utilisent SQLAlchemy
    avec la même syntaxe.
    Supporte les modèles utilisateur personnalisés avec colonnes supplémentaires.

    Attributes:
        db: Instance de connexion MySQL
        model_class: Classe du modèle utilisateur (par défaut ou personnalisée)
        mapper: Instance du mapper

    Example:
        ```python
        from sqlalchemy import Column, String
        from fastapi_acl.auth.infrastructure.models import SQLAuthUserModel

        class CustomUserModel(SQLAuthUserModel):
            __tablename__ = "users"
            phone = Column(String(20), nullable=True)

        repo = MySQLAuthRepository(
            db=database,
            model_class=CustomUserModel,
        )
        ```
    """

    def __init__(
        self,
        db: MySQLDatabase,
        model_class: Type[SQLAuthUserModel] = SQLAuthUserModel,
        mapper: Optional[AuthUserMapper] = None,
    ):
        """
        Initialise le repository.

        Args:
            db: Instance de MySQLDatabase
            model_class: Classe du modèle utilisateur (par défaut ou personnalisée)
            mapper: Instance du mapper personnalisée (optionnel)
        """
        # MySQLDatabase a la même interface que PostgreSQLDatabase
        super().__init__(db, model_class, mapper)  # type: ignore
