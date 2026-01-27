"""
Modèles SQLAlchemy pour les rôles (PostgreSQL/MySQL).
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, Table, ForeignKey, UniqueConstraint
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

    Ce modèle peut être étendu par le développeur pour ajouter
    des colonnes personnalisées via héritage.

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
        tenant_id: Identifiant du tenant (optionnel)
        created_at: Date de création
        updated_at: Date de mise à jour

    Example:
        Pour ajouter des colonnes personnalisées, créez une sous-classe:

        ```python
        from sqlalchemy import Column, String
        from alak_acl.roles.infrastructure.models import SQLRoleModel

        class CustomRoleModel(SQLRoleModel):
            __tablename__ = "custom_roles"
            department = Column(String(100), nullable=True)
        ```
    """

    __tablename__ = "acl_roles"

    @declared_attr
    def __tablename__(cls) -> str:
        return getattr(cls, '_custom_tablename', 'acl_roles')

    @declared_attr
    def __table_args__(cls):
        return (
            # Index unique composite : un nom de rôle est unique par tenant
            UniqueConstraint('tenant_id', 'name', name='uq_role_tenant_name'),
        )

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid_str,
        index=True,
    )
    name = Column(
        String(50),
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
    tenant_id = Column(
        String(36),
        nullable=True,
        index=True,
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

    # Relationship avec les utilisateurs via la table d'association
    users = relationship(
        "SQLAuthUserModel",
        secondary="acl_user_roles",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name})>"


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
