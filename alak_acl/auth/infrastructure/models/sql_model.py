"""
Modèle SQLAlchemy pour les utilisateurs (PostgreSQL/MySQL).

Ce module fournit un modèle de base extensible que le développeur
peut personnaliser en ajoutant ses propres colonnes.
"""

from datetime import datetime
from typing import Any, Dict, Type, Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import declared_attr

from alak_acl.shared.database.declarative_base import Base

# from ....shared.database.postgresql import Base


def generate_uuid_str() -> str:
    """Génère un UUID sous forme de string."""
    return str(uuid4())


class SQLAuthUserModel(Base):
    """
    Modèle SQLAlchemy de base pour la table des utilisateurs.

    Compatible PostgreSQL et MySQL.

    Ce modèle peut être étendu par le développeur pour ajouter
    des colonnes personnalisées.

    Attributes:
        id: Identifiant unique UUID (stocké en VARCHAR(36))
        username: Nom d'utilisateur unique
        email: Email unique
        hashed_password: Mot de passe hashé
        is_active: Compte actif
        is_verified: Email vérifié
        is_superuser: Administrateur
        created_at: Date de création
        updated_at: Date de mise à jour
        last_login: Dernière connexion
        extra_data: Champs personnalisés stockés en JSON

    Example:
        Pour ajouter des colonnes personnalisées, créez une sous-classe:

        ```python
        from sqlalchemy import Column, String, Integer
        from fastapi_acl.auth.infrastructure.models import SQLAuthUserModel

        class CustomUserModel(SQLAuthUserModel):
            __tablename__ = "users"  # Votre propre nom de table

            # Colonnes personnalisées
            phone = Column(String(20), nullable=True)
            company = Column(String(100), nullable=True)
            age = Column(Integer, nullable=True)
        ```
    """

    __tablename__ = "acl_auth_users"

    # Permet aux sous-classes de définir leur propre nom de table
    @declared_attr
    def __tablename__(cls) -> str:
        return getattr(cls, '_custom_tablename', 'acl_auth_users')

    # UUID stocké en VARCHAR(36) pour compatibilité PostgreSQL et MySQL
    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid_str,
        index=True,
    )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password = Column(
        String(255),
        nullable=False,
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    last_login = Column(
        DateTime,
        nullable=True,
    )
    # Champ JSON pour stocker des données supplémentaires flexibles
    # Utile pour les données non structurées
    extra_data = Column(
        JSON,
        nullable=True,
        default=dict,
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, username={self.username})>"

    def get_extra_columns(self) -> Dict[str, Any]:
        """
        Retourne les valeurs des colonnes personnalisées.

        Returns:
            Dictionnaire des colonnes non-standard
        """
        standard_columns = {
            'id', 'username', 'email', 'hashed_password',
            'is_active', 'is_verified', 'is_superuser',
            'created_at', 'updated_at', 'last_login', 'extra_data'
        }
        result = {}
        for column in self.__table__.columns:
            if column.name not in standard_columns:
                result[column.name] = getattr(self, column.name)
        return result

    @classmethod
    def get_custom_column_names(cls) -> list:
        """
        Retourne la liste des noms de colonnes personnalisées.

        Returns:
            Liste des noms de colonnes ajoutées par le développeur
        """
        standard_columns = {
            'id', 'username', 'email', 'hashed_password',
            'is_active', 'is_verified', 'is_superuser',
            'created_at', 'updated_at', 'last_login', 'extra_data'
        }
        return [
            col.name for col in cls.__table__.columns
            if col.name not in standard_columns
        ]


def create_user_model(
    tablename: str = "acl_auth_users",
    extra_columns: Optional[Dict[str, Column]] = None,
) -> Type[SQLAuthUserModel]:
    """
    Factory pour créer un modèle utilisateur personnalisé.

    Cette fonction permet de créer dynamiquement un modèle
    avec des colonnes supplémentaires sans créer de sous-classe.

    Args:
        tablename: Nom de la table
        extra_columns: Dictionnaire {nom: Column} des colonnes à ajouter

    Returns:
        Classe de modèle personnalisée

    Example:
        ```python
        from sqlalchemy import Column, String, Integer
        from fastapi_acl.auth.infrastructure.models import create_user_model

        CustomUser = create_user_model(
            tablename="users",
            extra_columns={
                "phone": Column(String(20), nullable=True),
                "company": Column(String(100), nullable=True),
                "age": Column(Integer, nullable=True),
            }
        )
        ```
    """
    # Créer les attributs de la nouvelle classe
    attrs = {
        '__tablename__': tablename,
        '__table_args__': {'extend_existing': True},
    }

    # Ajouter les colonnes personnalisées
    if extra_columns:
        attrs.update(extra_columns)

    # Créer la nouvelle classe dynamiquement
    CustomModel = type(
        'CustomAuthUserModel',
        (SQLAuthUserModel,),
        attrs
    )

    return CustomModel
