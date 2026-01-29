"""
Modèles SQLAlchemy pour les rôles et memberships (PostgreSQL/MySQL).

Le modèle Membership représente l'appartenance d'un utilisateur à un tenant
avec un rôle spécifique. C'est la table pivot du système SaaS multi-tenant.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from alak_acl.shared.database.declarative_base import Base


def generate_uuid_str() -> str:
    """Génère un UUID sous forme de string."""
    return str(uuid4())


class SQLRoleModel(Base):
    """
    Modèle SQLAlchemy pour la table des rôles.

    Compatible PostgreSQL et MySQL.

    Les rôles peuvent être:
    - Globaux (tenant_id=None): disponibles pour tous les tenants
    - Spécifiques à un tenant (tenant_id set): créés par l'app hôte pour un tenant

    Attributes:
        id: Identifiant unique (VARCHAR(36))
        name: Nom du rôle (unique par tenant ou globalement si tenant_id=None)
        display_name: Nom d'affichage
        description: Description du rôle
        permissions: Liste des permissions (JSON)
        is_active: Rôle actif
        is_default: Rôle par défaut pour les nouveaux membres
        is_system: Rôle système (non supprimable)
        priority: Priorité du rôle
        tenant_id: Identifiant du tenant (None = rôle global)
        created_at: Date de création
        updated_at: Date de mise à jour
    """

    __tablename__ = "acl_roles"
    __table_args__ = (
        # Index unique composite : un nom de rôle est unique par tenant
        # Si tenant_id=None, le nom est unique parmi les rôles globaux
        UniqueConstraint('tenant_id', 'name', name='uq_role_tenant_name'),
        {'extend_existing': True},
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

    # Relationship avec les memberships
    memberships = relationship(
        "SQLMembershipModel",
        back_populates="role",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name})>"


class SQLMembershipModel(Base):
    """
    Modèle pour la table de membership (pivot user-tenant-role).

    Représente l'appartenance d'un utilisateur à un tenant avec un rôle.
    C'est le cœur du système SaaS multi-tenant.

    Un utilisateur peut:
    - Appartenir à plusieurs tenants
    - Avoir plusieurs rôles dans un même tenant
    - Avoir des rôles différents selon le tenant

    Attributes:
        user_id: FK vers l'utilisateur
        tenant_id: ID du tenant (fourni par l'app hôte, pas de FK)
        role_id: FK vers le rôle
        assigned_at: Date d'assignation
        assigned_by: ID de l'utilisateur ayant fait l'assignation (optionnel)

    Note:
        tenant_id n'a pas de FK car les tenants sont gérés par l'app hôte,
        pas par le package ACL.
    """

    __tablename__ = "acl_memberships"
    __table_args__ = (
        # Un utilisateur ne peut avoir le même rôle qu'une fois par tenant
        UniqueConstraint('user_id', 'tenant_id', 'role_id', name='uq_membership'),
        {'extend_existing': True},
    )

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid_str,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey('acl_auth_users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        String(36),
        nullable=False,  # Obligatoire pour SaaS
        index=True,
    )
    role_id = Column(
        String(36),
        ForeignKey('acl_roles.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    assigned_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    assigned_by = Column(
        String(36),
        nullable=True,  # Optionnel: qui a assigné ce rôle
    )

    # Relationships
    user = relationship(
        "SQLAuthUserModel",
        back_populates="memberships",
    )
    role = relationship(
        "SQLRoleModel",
        back_populates="memberships",
    )

    def __repr__(self) -> str:
        return f"<Membership(user={self.user_id}, tenant={self.tenant_id}, role={self.role_id})>"


# Alias pour rétrocompatibilité (déprécié)
SQLUserRoleModel = SQLMembershipModel
