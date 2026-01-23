"""
Dépendances FastAPI pour la feature Roles.
"""

from typing import Optional, List
from functools import wraps

from fastapi import Depends, HTTPException, status

from ..application.interface.role_repository import IRoleRepository
from ..domain.entities.role import Role
from ...auth.domain.entities.auth_user import AuthUser
from ...auth.interface.dependencies import get_current_active_user


# Variable globale pour stocker le repository
_role_repository: Optional[IRoleRepository] = None


def set_role_dependencies(role_repository: IRoleRepository) -> None:
    """
    Configure les dépendances des rôles.

    À appeler lors de l'initialisation de l'application.

    Args:
        role_repository: Instance du repository des rôles
    """
    global _role_repository
    _role_repository = role_repository


def get_role_repository() -> IRoleRepository:
    """
    Retourne le repository des rôles.

    Raises:
        RuntimeError: Si le repository n'est pas configuré
    """
    if _role_repository is None:
        raise RuntimeError(
            "Role repository non configuré. "
            "Appelez set_role_dependencies() lors de l'initialisation."
        )
    return _role_repository


async def get_current_user_roles(
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> List[Role]:
    """
    Récupère les rôles de l'utilisateur courant.

    Returns:
        Liste des rôles de l'utilisateur
    """
    return await role_repository.get_user_roles(current_user.id)


async def get_current_user_permissions(
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> List[str]:
    """
    Récupère les permissions de l'utilisateur courant.

    Returns:
        Liste des permissions
    """
    return await role_repository.get_user_permissions(current_user.id)


class RequireRole:
    """
    Dépendance pour vérifier qu'un utilisateur a un rôle spécifique.

    Usage:
        @app.get("/admin")
        async def admin_route(
            user: AuthUser = Depends(RequireRole("admin"))
        ):
            ...
    """

    def __init__(self, role_name: str):
        """
        Args:
            role_name: Nom du rôle requis
        """
        self.role_name = role_name

    async def __call__(
        self,
        current_user: AuthUser = Depends(get_current_active_user),
        role_repository: IRoleRepository = Depends(get_role_repository),
    ) -> AuthUser:
        """
        Vérifie que l'utilisateur a le rôle.

        Raises:
            HTTPException: Si l'utilisateur n'a pas le rôle
        """
        # Les superusers ont toujours accès
        if current_user.is_superuser:
            return current_user

        has_role = await role_repository.user_has_role_by_name(
            current_user.id, self.role_name
        )

        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle requis: {self.role_name}",
            )

        return current_user


class RequireRoles:
    """
    Dépendance pour vérifier qu'un utilisateur a au moins un des rôles.

    Usage:
        @app.get("/moderator")
        async def mod_route(
            user: AuthUser = Depends(RequireRoles(["admin", "moderator"]))
        ):
            ...
    """

    def __init__(self, role_names: List[str], require_all: bool = False):
        """
        Args:
            role_names: Liste des noms de rôles
            require_all: Si True, tous les rôles sont requis
        """
        self.role_names = role_names
        self.require_all = require_all

    async def __call__(
        self,
        current_user: AuthUser = Depends(get_current_active_user),
        role_repository: IRoleRepository = Depends(get_role_repository),
    ) -> AuthUser:
        """
        Vérifie les rôles de l'utilisateur.

        Raises:
            HTTPException: Si les conditions ne sont pas remplies
        """
        if current_user.is_superuser:
            return current_user

        user_roles = await role_repository.get_user_roles(current_user.id)
        user_role_names = {role.name for role in user_roles}

        if self.require_all:
            # Tous les rôles sont requis
            if not all(name in user_role_names for name in self.role_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Tous les rôles requis: {', '.join(self.role_names)}",
                )
        else:
            # Au moins un rôle est requis
            if not any(name in user_role_names for name in self.role_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Un des rôles requis: {', '.join(self.role_names)}",
                )

        return current_user


class RequirePermission:
    """
    Dépendance pour vérifier qu'un utilisateur a une permission spécifique.

    Usage:
        @app.delete("/posts/{id}")
        async def delete_post(
            user: AuthUser = Depends(RequirePermission("posts:delete"))
        ):
            ...
    """

    def __init__(self, permission: str):
        """
        Args:
            permission: Permission requise
        """
        self.permission = permission

    async def __call__(
        self,
        current_user: AuthUser = Depends(get_current_active_user),
        role_repository: IRoleRepository = Depends(get_role_repository),
    ) -> AuthUser:
        """
        Vérifie que l'utilisateur a la permission.

        Raises:
            HTTPException: Si l'utilisateur n'a pas la permission
        """
        if current_user.is_superuser:
            return current_user

        roles = await role_repository.get_user_roles(current_user.id)

        for role in roles:
            if role.is_active and role.has_permission(self.permission):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission requise: {self.permission}",
        )


class RequirePermissions:
    """
    Dépendance pour vérifier qu'un utilisateur a les permissions spécifiées.

    Usage:
        @app.put("/posts/{id}")
        async def update_post(
            user: AuthUser = Depends(RequirePermissions(["posts:read", "posts:update"]))
        ):
            ...
    """

    def __init__(self, permissions: List[str], require_all: bool = True):
        """
        Args:
            permissions: Liste des permissions
            require_all: Si True, toutes les permissions sont requises
        """
        self.permissions = permissions
        self.require_all = require_all

    async def __call__(
        self,
        current_user: AuthUser = Depends(get_current_active_user),
        role_repository: IRoleRepository = Depends(get_role_repository),
    ) -> AuthUser:
        """
        Vérifie les permissions de l'utilisateur.

        Raises:
            HTTPException: Si les conditions ne sont pas remplies
        """
        if current_user.is_superuser:
            return current_user

        user_permissions = await role_repository.get_user_permissions(current_user.id)

        if self.require_all:
            missing = [p for p in self.permissions if p not in user_permissions]
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissions manquantes: {', '.join(missing)}",
                )
        else:
            if not any(p in user_permissions for p in self.permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Une des permissions requises: {', '.join(self.permissions)}",
                )

        return current_user


def require_role(role_name: str):
    """
    Décorateur pour protéger une route avec un rôle requis.

    Usage:
        @app.get("/admin")
        @require_role("admin")
        async def admin_route(current_user: AuthUser = Depends(get_current_active_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str):
    """
    Décorateur pour protéger une route avec une permission requise.

    Usage:
        @app.delete("/posts/{id}")
        @require_permission("posts:delete")
        async def delete_post(current_user: AuthUser = Depends(get_current_active_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
