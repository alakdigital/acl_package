"""
Modèle SQLAlchemy pour les permissions.

Compatible PostgreSQL et MySQL avec CHAR(36) pour les UUIDs.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    CHAR,
    Index,
)
from sqlalchemy.orm import Mapped

from alak_acl.shared.database.declarative_base import Base



def generate_uuid_str() -> str:
    """Génère un UUID sous forme de string."""
    return str(uuid4())


class SQLPermissionModel(Base):
    """
    Modèle SQLAlchemy pour les permissions.

    Représente une permission dans PostgreSQL ou MySQL.

    Attributes:
        id: UUID sous forme de CHAR(36)
        resource: Ressource concernée
        action: Action autorisée
        name: Nom complet (resource:action) - indexé, unique
        display_name: Nom d'affichage
        description: Description
        category: Catégorie pour regroupement
        is_active: Permission active
        is_system: Permission système (non supprimable)
        created_at: Date de création
        updated_at: Date de mise à jour
    """

    __tablename__ = "acl_permissions"

    id: Mapped[str] = Column(
        CHAR(36),
        primary_key=True,
        default=generate_uuid_str,
        index=True,
    )

    resource: Mapped[str] = Column(
        String(50),
        nullable=False,
        index=True,
    )

    action: Mapped[str] = Column(
        String(50),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = Column(
        String(101),  # resource(50) + ':' + action(50)
        nullable=False,
        unique=True,
        index=True,
    )

    display_name: Mapped[str] = Column(
        String(100),
        nullable=True,
    )

    description: Mapped[str] = Column(
        Text,
        nullable=True,
    )

    category: Mapped[str] = Column(
        String(50),
        nullable=True,
        index=True,
    )

    is_active: Mapped[bool] = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_system: Mapped[bool] = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = Column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow,
    )

    # Index composites pour les recherches fréquentes
    __table_args__ = (
        Index("idx_permission_resource_action", "resource", "action"),
        Index("idx_permission_category_active", "category", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<SQLPermissionModel(name='{self.name}', category='{self.category}')>"
