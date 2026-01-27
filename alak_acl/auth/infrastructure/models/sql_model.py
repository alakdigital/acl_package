"""
Modèle SQLAlchemy pour les utilisateurs (PostgreSQL/MySQL).

Ce module fournit un modèle de base extensible que le développeur
peut personnaliser en ajoutant ses propres colonnes via héritage.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import declared_attr, relationship

from alak_acl.shared.database.declarative_base import Base


def generate_uuid_str() -> str:
    """Génère un UUID sous forme de string."""
    return str(uuid4())


class SQLAuthUserModel(Base):
    """
    Modèle SQLAlchemy de base pour la table des utilisateurs.

    Compatible PostgreSQL et MySQL.

    Ce modèle peut être étendu par le développeur pour ajouter
    des colonnes personnalisées via héritage.

    Attributes:
        id: Identifiant unique UUID (stocké en VARCHAR(36))
        username: Nom d'utilisateur unique
        email: Email unique
        hashed_password: Mot de passe hashé
        is_active: Compte actif
        is_verified: Email vérifié
        is_superuser: Administrateur
        tenant_id: Identifiant du tenant (optionnel)
        created_at: Date de création
        updated_at: Date de mise à jour
        last_login: Dernière connexion

    Example:
        Pour ajouter des colonnes personnalisées, créez une sous-classe:

        ```python
        from sqlalchemy import Column, String, Integer
        from alak_acl.auth.infrastructure.models import SQLAuthUserModel

        class CustomUserModel(SQLAuthUserModel):
            __tablename__ = "users"

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

    @declared_attr
    def __table_args__(cls):
        return (
            # Index unique composite : username unique par tenant
            UniqueConstraint('tenant_id', 'username', name='uq_user_tenant_username'),
            # Index unique composite : email unique par tenant
            UniqueConstraint('tenant_id', 'email', name='uq_user_tenant_email'),
        )

    # UUID stocké en VARCHAR(36) pour compatibilité PostgreSQL et MySQL
    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid_str,
        index=True,
    )
    username = Column(
        String(50),
        nullable=False,
        index=True,
    )
    email = Column(
        String(255),
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
    last_login = Column(
        DateTime,
        nullable=True,
    )
    # Relationship avec les rôles via la table d'association
    roles = relationship(
        "SQLRoleModel",
        secondary="acl_user_roles",
        back_populates="users",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, username={self.username})>"
