"""
Use cases pour la gestion des permissions.

Contient la logique métier pour les opérations CRUD et de recherche.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from ..interface.permission_repository import IPermissionRepository
from ...domain.entities.permission import Permission
from ...domain.dtos.permission_dto import (
    CreatePermissionDTO,
    UpdatePermissionDTO,
    PermissionResponseDTO,
    PermissionListResponseDTO,
)
from ....shared.exceptions import PermissionNotFoundError, PermissionAlreadyExistsError
from ....shared.logging import logger


class CreatePermissionUseCase:
    """
    Use case pour créer une nouvelle permission.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(self, dto: CreatePermissionDTO) -> Permission:
        """
        Crée une nouvelle permission.

        Args:
            dto: Données de création

        Returns:
            Permission créée

        Raises:
            PermissionAlreadyExistsError: Si la permission existe déjà
        """
        permission = Permission(
            resource=dto.resource,
            action=dto.action,
            display_name=dto.display_name,
            description=dto.description,
            category=dto.category,
        )

        return await self._repository.create_permission(permission)


class UpdatePermissionUseCase:
    """
    Use case pour mettre à jour une permission.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(
        self,
        permission_id: str,
        dto: UpdatePermissionDTO,
    ) -> Permission:
        """
        Met à jour une permission existante.

        Args:
            permission_id: ID de la permission à mettre à jour
            dto: Données de mise à jour

        Returns:
            Permission mise à jour

        Raises:
            PermissionNotFoundError: Si la permission n'existe pas
        """
        permission = await self._repository.get_by_id(permission_id)
        if not permission:
            raise PermissionNotFoundError(f"Permission non trouvée: {permission_id}")

        # Mettre à jour les champs fournis
        if dto.display_name is not None:
            permission.display_name = dto.display_name
        if dto.description is not None:
            permission.description = dto.description
        if dto.category is not None:
            permission.category = dto.category
        if dto.is_active is not None:
            permission.is_active = dto.is_active

        permission.updated_at = datetime.utcnow()

        return await self._repository.update_permission(permission)


class DeletePermissionUseCase:
    """
    Use case pour supprimer une permission.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(self, permission_id: str) -> bool:
        """
        Supprime une permission.

        Args:
            permission_id: ID de la permission à supprimer

        Returns:
            True si supprimée

        Raises:
            PermissionNotFoundError: Si la permission n'existe pas
        """
        permission = await self._repository.get_by_id(permission_id)
        if not permission:
            raise PermissionNotFoundError(f"Permission non trouvée: {permission_id}")

        if permission.is_system:
            raise PermissionNotFoundError(
                "Impossible de supprimer une permission système"
            )

        return await self._repository.delete_permission(permission_id)


class GetPermissionUseCase:
    """
    Use case pour récupérer une permission.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(
        self,
        permission_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Permission:
        """
        Récupère une permission par ID ou nom.

        Args:
            permission_id: ID de la permission
            name: Nom de la permission (resource:action)

        Returns:
            Permission trouvée

        Raises:
            PermissionNotFoundError: Si non trouvée
            ValueError: Si aucun paramètre fourni
        """
        if permission_id:
            permission = await self._repository.get_by_id(permission_id)
        elif name:
            permission = await self._repository.get_by_name(name)
        else:
            raise ValueError("permission_id ou name requis")

        if not permission:
            raise PermissionNotFoundError(
                f"Permission non trouvée: {permission_id or name}"
            )

        return permission


class ListPermissionsUseCase:
    """
    Use case pour lister les permissions avec pagination.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> Tuple[List[Permission], int]:
        """
        Liste les permissions avec pagination et filtres.

        Args:
            skip: Offset de pagination
            limit: Limite de résultats
            is_active: Filtrer par statut actif
            category: Filtrer par catégorie
            resource: Filtrer par ressource

        Returns:
            Tuple (liste des permissions, total)
        """
        permissions = await self._repository.list_permissions(
            skip=skip,
            limit=limit,
            is_active=is_active,
            category=category,
            resource=resource,
        )

        total = await self._repository.count_permissions(
            is_active=is_active,
            category=category,
            resource=resource,
        )

        return permissions, total


class SearchPermissionsUseCase:
    """
    Use case pour rechercher des permissions.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Permission]:
        """
        Recherche des permissions par texte.

        Args:
            query: Texte de recherche
            skip: Offset de pagination
            limit: Limite de résultats

        Returns:
            Liste des permissions correspondantes
        """
        return await self._repository.search_permissions(
            query=query,
            skip=skip,
            limit=limit,
        )


class GetPermissionsByResourceUseCase:
    """
    Use case pour récupérer les permissions par ressource.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(self, resource: str) -> List[Permission]:
        """
        Récupère toutes les permissions d'une ressource.

        Args:
            resource: Nom de la ressource

        Returns:
            Liste des permissions
        """
        return await self._repository.get_by_resource(resource)


class GetPermissionsByCategoryUseCase:
    """
    Use case pour récupérer les permissions par catégorie.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(self, category: str) -> List[Permission]:
        """
        Récupère toutes les permissions d'une catégorie.

        Args:
            category: Nom de la catégorie

        Returns:
            Liste des permissions
        """
        return await self._repository.get_by_category(category)


class CreateBulkPermissionsUseCase:
    """
    Use case pour créer plusieurs permissions en une fois.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(
        self,
        permissions_data: List[CreatePermissionDTO],
    ) -> List[Permission]:
        """
        Crée plusieurs permissions.

        Args:
            permissions_data: Liste des données de création

        Returns:
            Liste des permissions créées (ignore les doublons)
        """
        permissions = [
            Permission(
                resource=dto.resource,
                action=dto.action,
                display_name=dto.display_name,
                description=dto.description,
                category=dto.category,
            )
            for dto in permissions_data
        ]

        return await self._repository.create_many(permissions)


class GetAllResourcesUseCase:
    """
    Use case pour récupérer toutes les ressources distinctes.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(self) -> List[str]:
        """
        Récupère la liste de toutes les ressources.

        Returns:
            Liste des noms de ressources
        """
        return await self._repository.get_all_resources()


class GetAllCategoriesUseCase:
    """
    Use case pour récupérer toutes les catégories distinctes.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self._repository = permission_repository

    async def execute(self) -> List[str]:
        """
        Récupère la liste de toutes les catégories.

        Returns:
            Liste des noms de catégories
        """
        return await self._repository.get_all_categories()
