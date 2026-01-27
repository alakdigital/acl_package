"""
Use cases pour la gestion des rôles.
"""

from datetime import datetime
from typing import List, Optional

from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.roles.domain.dtos.role_dto import CreateRoleDTO, UpdateRoleDTO
from alak_acl.roles.domain.entities.role import Role
from alak_acl.shared.exceptions import RoleAlreadyExistsError, RoleNotFoundError



class CreateRoleUseCase:
    """Use case pour créer un nouveau rôle."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, dto: CreateRoleDTO) -> Role:
        """
        Crée un nouveau rôle.

        Args:
            dto: Données du rôle à créer

        Returns:
            Rôle créé

        Raises:
            RoleAlreadyExistsError: Si un rôle avec ce nom existe déjà
        """
        # Vérifier si le nom existe déjà
        if await self._role_repository.role_exists(dto.name):
            raise RoleAlreadyExistsError(f"Un rôle avec le nom '{dto.name}' existe déjà")

        role = Role(
            name=dto.name,
            display_name=dto.display_name,
            description=dto.description,
            permissions=dto.permissions,
            is_default=dto.is_default,
            priority=dto.priority,
            tenant_id=dto.tenant_id,
        )

        return await self._role_repository.create_role(role)


class UpdateRoleUseCase:
    """Use case pour mettre à jour un rôle."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, role_id: str, dto: UpdateRoleDTO) -> Role:
        """
        Met à jour un rôle.

        Args:
            role_id: ID du rôle
            dto: Données à mettre à jour

        Returns:
            Rôle mis à jour

        Raises:
            RoleNotFoundError: Si le rôle n'existe pas
        """
        role = await self._role_repository.get_by_id(role_id)
        if not role:
            raise RoleNotFoundError(f"Rôle non trouvé: {role_id}")

        # Mettre à jour les champs fournis
        if dto.display_name is not None:
            role.display_name = dto.display_name
        if dto.description is not None:
            role.description = dto.description
        if dto.permissions is not None:
            role.permissions = dto.permissions
        if dto.is_active is not None:
            role.is_active = dto.is_active
        if dto.is_default is not None:
            role.is_default = dto.is_default
        if dto.priority is not None:
            role.priority = dto.priority
        if dto.tenant_id is not None:
            role.tenant_id = dto.tenant_id

        role.updated_at = datetime.utcnow()

        return await self._role_repository.update_role(role)


class DeleteRoleUseCase:
    """Use case pour supprimer un rôle."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, role_id: str) -> bool:
        """
        Supprime un rôle.

        Args:
            role_id: ID du rôle

        Returns:
            True si supprimé

        Raises:
            RoleNotFoundError: Si le rôle n'existe pas
            PermissionDeniedError: Si c'est un rôle système
        """
        return await self._role_repository.delete_role(role_id)


class GetRoleUseCase:
    """Use case pour récupérer un rôle."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute_by_id(self, role_id: str) -> Optional[Role]:
        """Récupère un rôle par son ID."""
        return await self._role_repository.get_by_id(role_id)

    async def execute_by_name(self, name: str) -> Optional[Role]:
        """Récupère un rôle par son nom."""
        return await self._role_repository.get_by_name(name)


class ListRolesUseCase:
    """Use case pour lister les rôles."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Role], int]:
        """
        Liste les rôles avec pagination.

        Returns:
            Tuple (liste des rôles, total)
        """
        roles = await self._role_repository.list_roles(
            skip=skip,
            limit=limit,
            is_active=is_active,
        )
        total = await self._role_repository.count_roles(is_active=is_active)
        return roles, total


class AssignRoleUseCase:
    """Use case pour assigner un rôle à un utilisateur."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str, role_id: str) -> bool:
        """
        Assigne un rôle à un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            role_id: ID du rôle

        Returns:
            True si assigné

        Raises:
            RoleNotFoundError: Si le rôle n'existe pas
        """
        return await self._role_repository.assign_role_to_user(user_id, role_id)

    async def execute_by_name(self, user_id: str, role_name: str) -> bool:
        """
        Assigne un rôle par son nom.

        Args:
            user_id: ID de l'utilisateur
            role_name: Nom du rôle

        Returns:
            True si assigné

        Raises:
            RoleNotFoundError: Si le rôle n'existe pas
        """
        role = await self._role_repository.get_by_name(role_name)
        if not role:
            raise RoleNotFoundError(f"Rôle non trouvé: {role_name}")
        return await self._role_repository.assign_role_to_user(user_id, role.id)


class RemoveRoleUseCase:
    """Use case pour retirer un rôle d'un utilisateur."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str, role_id: str) -> bool:
        """
        Retire un rôle d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            role_id: ID du rôle

        Returns:
            True si retiré
        """
        return await self._role_repository.remove_role_from_user(user_id, role_id)


class GetUserRolesUseCase:
    """Use case pour récupérer les rôles d'un utilisateur."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str) -> List[Role]:
        """
        Récupère les rôles d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Liste des rôles
        """
        return await self._role_repository.get_user_roles(user_id)


class GetUserPermissionsUseCase:
    """Use case pour récupérer les permissions d'un utilisateur."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str) -> List[str]:
        """
        Récupère toutes les permissions d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Liste des permissions uniques
        """
        return await self._role_repository.get_user_permissions(user_id)


class CheckPermissionUseCase:
    """Use case pour vérifier si un utilisateur a une permission."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str, permission: str) -> bool:
        """
        Vérifie si un utilisateur a une permission.

        Args:
            user_id: ID de l'utilisateur
            permission: Permission à vérifier

        Returns:
            True si l'utilisateur a la permission
        """
        roles = await self._role_repository.get_user_roles(user_id)
        for role in roles:
            if role.is_active and role.has_permission(permission):
                return True
        return False


class CheckRoleUseCase:
    """Use case pour vérifier si un utilisateur a un rôle."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str, role_id: str) -> bool:
        """Vérifie si un utilisateur a un rôle par ID."""
        return await self._role_repository.user_has_role(user_id, role_id)

    async def execute_by_name(self, user_id: str, role_name: str) -> bool:
        """Vérifie si un utilisateur a un rôle par nom."""
        return await self._role_repository.user_has_role_by_name(user_id, role_name)


class SetUserRolesUseCase:
    """Use case pour définir la liste complète des rôles d'un utilisateur."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str, role_ids: List[str]) -> bool:
        """
        Définit tous les rôles d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            role_ids: Liste des IDs de rôles

        Returns:
            True si succès
        """
        return await self._role_repository.set_user_roles(user_id, role_ids)


class AssignDefaultRolesUseCase:
    """Use case pour assigner les rôles par défaut à un nouvel utilisateur."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repository = role_repository

    async def execute(self, user_id: str) -> List[Role]:
        """
        Assigne les rôles par défaut à un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Liste des rôles assignés
        """
        default_roles = await self._role_repository.get_default_roles()

        for role in default_roles:
            await self._role_repository.assign_role_to_user(user_id, role.id)

        return default_roles
