"""
Interface du repository des rôles.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from alak_acl.roles.domain.entities.role import Role



class IRoleRepository(ABC):
    """
    Interface abstraite pour le repository des rôles.

    Définit le contrat que chaque implémentation de repository
    (MongoDB, PostgreSQL, MySQL) doit respecter.
    """

    # ==========================================
    # CRUD Rôles
    # ==========================================

    @abstractmethod
    async def create_role(self, role: Role) -> Role:
        """
        Crée un nouveau rôle.

        Args:
            role: Entité rôle à créer

        Returns:
            Rôle créé avec son ID

        Raises:
            RoleAlreadyExistsError: Si un rôle avec ce nom existe déjà
        """
        pass

    @abstractmethod
    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """
        Récupère un rôle par son ID.

        Args:
            role_id: ID du rôle

        Returns:
            Rôle ou None si non trouvé
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Récupère un rôle par son nom.

        Args:
            name: Nom du rôle

        Returns:
            Rôle ou None si non trouvé
        """
        pass

    @abstractmethod
    async def update_role(self, role: Role) -> Role:
        """
        Met à jour un rôle existant.

        Args:
            role: Entité rôle avec les modifications

        Returns:
            Rôle mis à jour

        Raises:
            RoleNotFoundError: Si le rôle n'existe pas
        """
        pass

    @abstractmethod
    async def delete_role(self, role_id: str) -> bool:
        """
        Supprime un rôle.

        Args:
            role_id: ID du rôle

        Returns:
            True si supprimé, False si non trouvé

        Raises:
            PermissionDeniedError: Si le rôle est un rôle système
        """
        pass

    @abstractmethod
    async def list_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Role]:
        """
        Liste les rôles avec pagination.

        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments
            is_active: Filtrer par statut actif (optionnel)
            tenant_id: Filtrer par tenant (optionnel)

        Returns:
            Liste des rôles
        """
        pass

    @abstractmethod
    async def count_roles(
        self,
        is_active: Optional[bool] = None,
        tenant_id: Optional[str] = None,
    ) -> int:
        """
        Compte le nombre de rôles.

        Args:
            is_active: Filtrer par statut actif (optionnel)
            tenant_id: Filtrer par tenant (optionnel)

        Returns:
            Nombre de rôles
        """
        pass

    @abstractmethod
    async def role_exists(self, name: str) -> bool:
        """
        Vérifie si un rôle existe par son nom.

        Args:
            name: Nom du rôle

        Returns:
            True si existe
        """
        pass

    @abstractmethod
    async def get_default_roles(self) -> List[Role]:
        """
        Récupère tous les rôles par défaut.

        Returns:
            Liste des rôles marqués comme default
        """
        pass

    @abstractmethod
    async def get_default_role(self) -> Optional[Role]:
        """
        Récupère le rôle par défaut (premier rôle marqué is_default=True).

        Returns:
            Rôle par défaut ou None
        """
        pass

    # ==========================================
    # Memberships (user <-> tenant <-> role)
    # ==========================================

    @abstractmethod
    async def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
        assigned_by: Optional[str] = None,
    ) -> bool:
        """
        Assigne un rôle à un utilisateur dans un tenant (crée un membership).

        Args:
            user_id: ID de l'utilisateur
            role_id: ID du rôle
            tenant_id: ID du tenant (fourni par l'app hôte)
            assigned_by: ID de l'utilisateur ayant fait l'assignation (optionnel)

        Returns:
            True si assigné avec succès

        Raises:
            RoleNotFoundError: Si le rôle n'existe pas
        """
        pass

    @abstractmethod
    async def remove_role_from_user(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Retire un rôle d'un utilisateur dans un tenant.

        Args:
            user_id: ID de l'utilisateur
            role_id: ID du rôle
            tenant_id: ID du tenant

        Returns:
            True si retiré avec succès
        """
        pass

    @abstractmethod
    async def get_user_roles(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
    ) -> List[Role]:
        """
        Récupère les rôles d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            tenant_id: ID du tenant (si None, retourne les rôles de tous les tenants)

        Returns:
            Liste des rôles de l'utilisateur
        """
        pass

    @abstractmethod
    async def get_user_tenants(self, user_id: str) -> List[str]:
        """
        Récupère les IDs des tenants auxquels un utilisateur appartient.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Liste des IDs de tenants
        """
        pass

    @abstractmethod
    async def get_users_with_role(
        self,
        role_id: str,
        tenant_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """
        Récupère les IDs des utilisateurs ayant un rôle spécifique.

        Args:
            role_id: ID du rôle
            tenant_id: ID du tenant (si None, cherche dans tous les tenants)
            skip: Offset pour la pagination
            limit: Limite du nombre de résultats

        Returns:
            Liste des IDs utilisateurs
        """
        pass

    @abstractmethod
    async def user_has_role(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Vérifie si un utilisateur a un rôle dans un tenant.

        Args:
            user_id: ID de l'utilisateur
            role_id: ID du rôle
            tenant_id: ID du tenant

        Returns:
            True si l'utilisateur a le rôle dans ce tenant
        """
        pass

    @abstractmethod
    async def user_has_role_by_name(
        self,
        user_id: str,
        role_name: str,
        tenant_id: str,
    ) -> bool:
        """
        Vérifie si un utilisateur a un rôle par son nom dans un tenant.

        Args:
            user_id: ID de l'utilisateur
            role_name: Nom du rôle
            tenant_id: ID du tenant

        Returns:
            True si l'utilisateur a le rôle dans ce tenant
        """
        pass

    @abstractmethod
    async def get_user_permissions(
        self,
        user_id: str,
        tenant_id: str,
    ) -> List[str]:
        """
        Récupère toutes les permissions d'un utilisateur dans un tenant.

        Args:
            user_id: ID de l'utilisateur
            tenant_id: ID du tenant

        Returns:
            Liste des permissions uniques
        """
        pass

    @abstractmethod
    async def set_user_roles(
        self,
        user_id: str,
        role_ids: List[str],
        tenant_id: str,
    ) -> bool:
        """
        Définit la liste complète des rôles d'un utilisateur dans un tenant.

        Remplace tous les rôles existants dans ce tenant.

        Args:
            user_id: ID de l'utilisateur
            role_ids: Liste des IDs de rôles
            tenant_id: ID du tenant

        Returns:
            True si succès
        """
        pass

    @abstractmethod
    async def clear_user_roles(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """
        Supprime les rôles d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            tenant_id: ID du tenant (si None, supprime dans tous les tenants)

        Returns:
            True si succès
        """
        pass

    @abstractmethod
    async def get_tenant_members(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """
        Récupère les IDs des utilisateurs membres d'un tenant.

        Args:
            tenant_id: ID du tenant
            skip: Offset pour la pagination
            limit: Limite du nombre de résultats

        Returns:
            Liste des IDs utilisateurs
        """
        pass

    @abstractmethod
    async def count_tenant_members(self, tenant_id: str) -> int:
        """
        Compte le nombre de membres d'un tenant.

        Args:
            tenant_id: ID du tenant

        Returns:
            Nombre de membres
        """
        pass

    # ==========================================
    # Vérifications pour la suppression
    # ==========================================

    @abstractmethod
    async def count_roles_with_permission(self, permission_name: str) -> int:
        """
        Compte le nombre de rôles qui utilisent une permission.

        Args:
            permission_name: Nom de la permission (ex: "posts:create")

        Returns:
            Nombre de rôles utilisant cette permission
        """
        pass
