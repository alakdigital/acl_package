"""
Modèles SQLAlchemy pour les rôles (PostgreSQL/MySQL).
"""

from datetime import datetime
from typing import Any, Dict, List, Type, Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, Table, ForeignKey
from sqlalchemy.orm import declared_attr, relationship

from alak_acl.shared.database.declarative_base import Base


def generate_uuid_str() -> str:
    """Génère un UUID sous forme de string."""
    return str(uuid4())


# Table d'association user_roles (many-to-many)
user_roles_table = Table(
    'acl_user_roles',
    Base.metadata,
    Column('user_id', String(36), ForeignKey('acl_auth_users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', String(36), ForeignKey('acl_roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow, nullable=False),
)


class SQLRoleModel(Base):
    """
    Modèle SQLAlchemy pour la table des rôles.

    Compatible PostgreSQL et MySQL.

    Attributes:
        id: Identifiant unique (VARCHAR(36))
        name: Nom unique du rôle
        display_name: Nom d'affichage
        description: Description du rôle
        permissions: Liste des permissions (JSON)
        is_active: Rôle actif
        is_default: Rôle par défaut
        is_system: Rôle système (non supprimable)
        priority: Priorité du rôle
        created_at: Date de création
        updated_at: Date de mise à jour
        metadata: Métadonnées additionnelles (JSON)

    Example:
        ```python
        from sqlalchemy import Column, String
        from fastapi_acl.roles.infrastructure.models import SQLRoleModel

        class CustomRoleModel(SQLRoleModel):
            __tablename__ = "custom_roles"
            department = Column(String(100), nullable=True)
        ```
    """

    __tablename__ = "acl_roles"

    @declared_attr
    def __tablename__(cls) -> str:
        return getattr(cls, '_custom_tablename', 'acl_roles')

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid_str,
        index=True,
    )
    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name = Column(
        String(100),
        nullable=True,
    )
    description = Column(
        String(500),
        nullable=True,
    )
    permissions = Column(
        JSON,
        nullable=False,
        default=list,
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    is_system = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    priority = Column(
        Integer,
        default=0,
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
    metadata_ = Column(
        "metadata",
        JSON,
        nullable=True,
        default=dict,
    )

    def __repr__(self) -> str:
        return f"<SQLRoleModel(id={self.id}, name={self.name})>"

    def get_extra_columns(self) -> Dict[str, Any]:
        """Retourne les valeurs des colonnes personnalisées."""
        standard_columns = {
            'id', 'name', 'display_name', 'description', 'permissions',
            'is_active', 'is_default', 'is_system', 'priority',
            'created_at', 'updated_at', 'metadata', 'metadata_'
        }
        result = {}
        for column in self.__table__.columns:
            if column.name not in standard_columns:
                result[column.name] = getattr(self, column.name)
        return result

    @classmethod
    def get_custom_column_names(cls) -> list:
        """Retourne la liste des noms de colonnes personnalisées."""
        standard_columns = {
            'id', 'name', 'display_name', 'description', 'permissions',
            'is_active', 'is_default', 'is_system', 'priority',
            'created_at', 'updated_at', 'metadata', 'metadata_'
        }
        return [
            col.name for col in cls.__table__.columns
            if col.name not in standard_columns
        ]


class SQLUserRoleModel(Base):
    """
    Modèle pour la table d'association user_roles.

    Utilisé pour les requêtes explicites sur la relation.
    """

    __tablename__ = "acl_user_roles"
    __table_args__ = {'extend_existing': True}

    user_id = Column(
        String(36),
        ForeignKey('acl_auth_users.id', ondelete='CASCADE'),
        primary_key=True,
    )
    role_id = Column(
        String(36),
        ForeignKey('acl_roles.id', ondelete='CASCADE'),
        primary_key=True,
    )
    assigned_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


def create_role_model(
    tablename: str = "acl_roles",
    extra_columns: Optional[Dict[str, Column]] = None,
) -> Type[SQLRoleModel]:
    """
    Factory pour créer un modèle rôle personnalisé.

    Args:
        tablename: Nom de la table
        extra_columns: Dictionnaire {nom: Column} des colonnes à ajouter

    Returns:
        Classe de modèle personnalisée
    """
    attrs = {
        '__tablename__': tablename,
        '__table_args__': {'extend_existing': True},
    }

    if extra_columns:
        attrs.update(extra_columns)

    CustomModel = type(
        'CustomRoleModel',
        (SQLRoleModel,),
        attrs
    )

    return CustomModel
