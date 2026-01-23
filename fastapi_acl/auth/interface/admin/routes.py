"""
Routes d'administration pour la gestion des utilisateurs.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from ...domain.entities.auth_user import AuthUser
from ...application.interface.auth_repository import IAuthRepository
from ..schemas import (
    UserResponse,
    UserListResponse,
    UpdateUserRequest,
    MessageResponse,
)
from ..dependencies import (
    get_auth_repository,
    get_current_superuser,
)
from ....shared.exceptions import UserNotFoundError
from ....shared.logging import logger


router = APIRouter(prefix="/admin/auth", tags=["Admin - Authentication"])


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="Lister les utilisateurs",
    description="Liste tous les utilisateurs avec pagination (admin uniquement).",
)
async def list_users(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum d'éléments"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    current_user: AuthUser = Depends(get_current_superuser),
    auth_repository: IAuthRepository = Depends(get_auth_repository),
) -> UserListResponse:
    """
    Liste les utilisateurs avec pagination.

    Args:
        skip: Offset pour la pagination
        limit: Limite du nombre de résultats
        is_active: Filtre optionnel sur le statut actif
        current_user: Administrateur authentifié
        auth_repository: Repository d'authentification

    Returns:
        Liste paginée des utilisateurs
    """
    users = await auth_repository.list_users(
        skip=skip,
        limit=limit,
        is_active=is_active,
    )
    total = await auth_repository.count_users(is_active=is_active)

    return UserListResponse(
        users=[
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                is_verified=user.is_verified,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                last_login=user.last_login,
            )
            for user in users
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Détails d'un utilisateur",
    description="Récupère les détails d'un utilisateur par son ID (admin uniquement).",
)
async def get_user(
    user_id: UUID,
    current_user: AuthUser = Depends(get_current_superuser),
    auth_repository: IAuthRepository = Depends(get_auth_repository),
) -> UserResponse:
    """
    Récupère un utilisateur par son ID.

    Args:
        user_id: ID de l'utilisateur
        current_user: Administrateur authentifié
        auth_repository: Repository d'authentification

    Returns:
        Détails de l'utilisateur
    """
    user = await auth_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.put(
    "/users/{user_id}/activate",
    response_model=UserResponse,
    summary="Activer un utilisateur",
    description="Active un compte utilisateur désactivé (admin uniquement).",
)
async def activate_user(
    user_id: UUID,
    current_user: AuthUser = Depends(get_current_superuser),
    auth_repository: IAuthRepository = Depends(get_auth_repository),
) -> UserResponse:
    """
    Active un compte utilisateur.

    Args:
        user_id: ID de l'utilisateur
        current_user: Administrateur authentifié
        auth_repository: Repository d'authentification

    Returns:
        Utilisateur activé
    """
    user = await auth_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    user.activate()
    updated_user = await auth_repository.update_user(user)

    logger.info(f"Utilisateur activé par {current_user.username}: {user.username}")

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        is_superuser=updated_user.is_superuser,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login,
    )


@router.put(
    "/users/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Désactiver un utilisateur",
    description="Désactive un compte utilisateur (admin uniquement).",
)
async def deactivate_user(
    user_id: UUID,
    current_user: AuthUser = Depends(get_current_superuser),
    auth_repository: IAuthRepository = Depends(get_auth_repository),
) -> UserResponse:
    """
    Désactive un compte utilisateur.

    Args:
        user_id: ID de l'utilisateur
        current_user: Administrateur authentifié
        auth_repository: Repository d'authentification

    Returns:
        Utilisateur désactivé
    """
    user = await auth_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    # Empêcher la désactivation de son propre compte
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas désactiver votre propre compte",
        )

    user.deactivate()
    updated_user = await auth_repository.update_user(user)

    logger.info(f"Utilisateur désactivé par {current_user.username}: {user.username}")

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        is_superuser=updated_user.is_superuser,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login,
    )


@router.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
    summary="Supprimer un utilisateur",
    description="Supprime définitivement un compte utilisateur (admin uniquement).",
)
async def delete_user(
    user_id: UUID,
    current_user: AuthUser = Depends(get_current_superuser),
    auth_repository: IAuthRepository = Depends(get_auth_repository),
) -> MessageResponse:
    """
    Supprime un utilisateur.

    Args:
        user_id: ID de l'utilisateur
        current_user: Administrateur authentifié
        auth_repository: Repository d'authentification

    Returns:
        Message de confirmation
    """
    # Empêcher la suppression de son propre compte
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte",
        )

    user = await auth_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    deleted = await auth_repository.delete_user(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression",
        )

    logger.info(f"Utilisateur supprimé par {current_user.username}: {user.username}")

    return MessageResponse(
        message=f"Utilisateur '{user.username}' supprimé avec succès",
        success=True,
    )
