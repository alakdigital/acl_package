"""
Interface du repository des permissions.

Définit le contrat que doivent implémenter tous les repositories
de permissions (PostgreSQL, MySQL, MongoDB).
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from alak_acl.permissions.domain.entities.permission import Permission



class IPermissionRepository(ABC):
    """
    Interface abstraite pour le repository des permissions.

    Définit les opérations CRUD et de recherche sur les permissions.
    """

    # ============================================
    # CRUD Operations
    # ============================================

    @abstractmethod
    async def create_permission(self, permission: Permission) -> Permission:
        """
        Crée une nouvelle permission.

        Args:
            permission: Entité Permission à créer

        Returns:
            Permission créée avec son ID

        Raises:
            PermissionAlreadyExistsError: Si une permission avec ce nom existe
        """
        pass

    @abstractmethod
    async def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """
        Récupère une permission par son ID.

        Args:
            permission_id: ID de la permission

        Returns:
            Permission trouvée ou None
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Permission]:
        """
        Récupère une permission par son nom (resource:action).

        Args:
            name: Nom de la permission (ex: "posts:create")

        Returns:
            Permission trouvée ou None
        """
        pass

    @abstractmethod
    async def update_permission(self, permission: Permission) -> Permission:
        """
        Met à jour une permission existante.

        Args:
            permission: Entité Permission avec les nouvelles valeurs

        Returns:
            Permission mise à jour

        Raises:
            PermissionNotFoundError: Si la permission n'existe pas
        """
        pass

    @abstractmethod
    async def delete_permission(self, permission_id: str) -> bool:
        """
        Supprime une permission.

        Args:
            permission_id: ID de la permission à supprimer

        Returns:
            True si supprimée, False sinon

        Raises:
            PermissionNotFoundError: Si la permission n'existe pas
        """
        pass

    # ============================================
    # Query Operations
    # ============================================

    @abstractmethod
    async def list_permissions(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> List[Permission]:
        """
        Liste les permissions avec pagination et filtres.

        Args:
            skip: Offset pour la pagination
            limit: Limite de résultats
            is_active: Filtrer par statut actif
            category: Filtrer par catégorie
            resource: Filtrer par ressource

        Returns:
            Liste des permissions
        """
        pass

    @abstractmethod
    async def count_permissions(
        self,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> int:
        """
        Compte le nombre de permissions.

        Args:
            is_active: Filtrer par statut actif
            category: Filtrer par catégorie
            resource: Filtrer par ressource

        Returns:
            Nombre de permissions
        """
        pass

    @abstractmethod
    async def get_by_resource(self, resource: str) -> List[Permission]:
        """
        Récupère toutes les permissions d'une ressource.

        Args:
            resource: Nom de la ressource

        Returns:
            Liste des permissions de cette ressource
        """
        pass

    @abstractmethod
    async def get_by_category(self, category: str) -> List[Permission]:
        """
        Récupère toutes les permissions d'une catégorie.

        Args:
            category: Nom de la catégorie

        Returns:
            Liste des permissions de cette catégorie
        """
        pass

    @abstractmethod
    async def get_all_resources(self) -> List[str]:
        """
        Récupère la liste de toutes les ressources distinctes.

        Returns:
            Liste des noms de ressources
        """
        pass

    @abstractmethod
    async def get_all_categories(self) -> List[str]:
        """
        Récupère la liste de toutes les catégories distinctes.

        Returns:
            Liste des noms de catégories
        """
        pass

    # ============================================
    # Bulk Operations
    # ============================================

    @abstractmethod
    async def create_many(self, permissions: List[Permission]) -> List[Permission]:
        """
        Crée plusieurs permissions en une seule opération.

        Args:
            permissions: Liste des permissions à créer

        Returns:
            Liste des permissions créées
        """
        pass

    @abstractmethod
    async def get_by_ids(self, permission_ids: List[str]) -> List[Permission]:
        """
        Récupère plusieurs permissions par leurs IDs.

        Args:
            permission_ids: Liste des IDs

        Returns:
            Liste des permissions trouvées
        """
        pass

    @abstractmethod
    async def get_by_names(self, names: List[str]) -> List[Permission]:
        """
        Récupère plusieurs permissions par leurs noms.

        Args:
            names: Liste des noms (format "resource:action")

        Returns:
            Liste des permissions trouvées
        """
        pass

    # ============================================
    # Utility Methods
    # ============================================

    @abstractmethod
    async def permission_exists(self, name: str) -> bool:
        """
        Vérifie si une permission existe par son nom.

        Args:
            name: Nom de la permission (resource:action)

        Returns:
            True si elle existe
        """
        pass

    @abstractmethod
    async def search_permissions(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Permission]:
        """
        Recherche des permissions par texte.

        Recherche dans name, display_name, description.

        Args:
            query: Texte de recherche
            skip: Offset pour la pagination
            limit: Limite de résultats

        Returns:
            Liste des permissions correspondantes
        """
        pass
