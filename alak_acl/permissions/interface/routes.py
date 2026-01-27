"""
Routes API pour la feature Permissions.

Fournit les endpoints REST pour la gestion des permissions.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query

from alak_acl.permissions.application.interface.permission_repository import IPermissionRepository
from alak_acl.permissions.application.usecases.permission_usecases import (
    CreatePermissionUseCase,
    UpdatePermissionUseCase,
    DeletePermissionUseCase,
    GetPermissionUseCase,
    ListPermissionsUseCase,
    SearchPermissionsUseCase,
    GetPermissionsByResourceUseCase,
    GetPermissionsByCategoryUseCase,
    CreateBulkPermissionsUseCase,
)
from alak_acl.permissions.domain.dtos.permission_dto import (
    CreatePermissionDTO,
    UpdatePermissionDTO,
    PermissionResponseDTO,
    PermissionListResponseDTO,
)
from alak_acl.permissions.domain.entities.permission import Permission
from alak_acl.permissions.interface.dependencies import get_permission_repository
from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.roles.interface.dependencies import get_role_repository
from alak_acl.auth.interface.dependencies import get_current_superuser
from alak_acl.shared.exceptions import (
    PermissionNotFoundError,
    PermissionAlreadyExistsError,
    PermissionInUseError,
)


router = APIRouter(prefix="/permissions", tags=["Permissions"])


def _to_response_dto(permission: Permission) -> PermissionResponseDTO:
    """Convertit une entité Permission en DTO de réponse."""
    return PermissionResponseDTO(
        id=permission.id,
        resource=permission.resource,
        action=permission.action,
        name=permission.name,
        display_name=permission.display_name,
        description=permission.description,
        category=permission.category,
        is_active=permission.is_active,
        is_system=permission.is_system,
        created_at=permission.created_at,
        updated_at=permission.updated_at,
    )


# ============================================
# Endpoints de lecture (tous les utilisateurs authentifiés)
# ============================================

@router.get(
    "",
    response_model=PermissionListResponseDTO,
    summary="Lister les permissions",
    description="Récupère la liste des permissions avec pagination et filtres.",
)
async def list_permissions(
    skip: int = Query(0, ge=0, description="Offset de pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limite de résultats"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    resource: Optional[str] = Query(None, description="Filtrer par ressource"),
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Liste les permissions avec pagination et filtres."""
    usecase = ListPermissionsUseCase(repository)
    permissions, total = await usecase.execute(
        skip=skip,
        limit=limit,
        is_active=is_active,
        category=category,
        resource=resource,
    )

    return PermissionListResponseDTO(
        permissions=[_to_response_dto(p) for p in permissions],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/search",
    response_model=List[PermissionResponseDTO],
    summary="Rechercher des permissions",
    description="Recherche des permissions par texte dans le nom, display_name ou description.",
)
async def search_permissions(
    q: str = Query(..., min_length=1, description="Texte de recherche"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Recherche des permissions par texte."""
    usecase = SearchPermissionsUseCase(repository)
    permissions = await usecase.execute(query=q, skip=skip, limit=limit)
    return [_to_response_dto(p) for p in permissions]


@router.get(
    "/resources",
    response_model=List[str],
    summary="Lister les ressources",
    description="Récupère la liste de toutes les ressources distinctes.",
)
async def list_resources(
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Liste toutes les ressources distinctes."""
    return await repository.get_all_resources()


@router.get(
    "/categories",
    response_model=List[str],
    summary="Lister les catégories",
    description="Récupère la liste de toutes les catégories distinctes.",
)
async def list_categories(
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Liste toutes les catégories distinctes."""
    return await repository.get_all_categories()


@router.get(
    "/resource/{resource}",
    response_model=List[PermissionResponseDTO],
    summary="Permissions par ressource",
    description="Récupère toutes les permissions d'une ressource.",
)
async def get_permissions_by_resource(
    resource: str,
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Récupère les permissions d'une ressource."""
    usecase = GetPermissionsByResourceUseCase(repository)
    permissions = await usecase.execute(resource)
    return [_to_response_dto(p) for p in permissions]


@router.get(
    "/category/{category}",
    response_model=List[PermissionResponseDTO],
    summary="Permissions par catégorie",
    description="Récupère toutes les permissions d'une catégorie.",
)
async def get_permissions_by_category(
    category: str,
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Récupère les permissions d'une catégorie."""
    usecase = GetPermissionsByCategoryUseCase(repository)
    permissions = await usecase.execute(category)
    return [_to_response_dto(p) for p in permissions]


@router.get(
    "/{permission_id}",
    response_model=PermissionResponseDTO,
    summary="Détails d'une permission",
    description="Récupère les détails d'une permission par son ID.",
)
async def get_permission(
    permission_id: str,
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Récupère une permission par son ID."""
    usecase = GetPermissionUseCase(repository)
    try:
        permission = await usecase.execute(permission_id=permission_id)
        return _to_response_dto(permission)
    except PermissionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/name/{name:path}",
    response_model=PermissionResponseDTO,
    summary="Permission par nom",
    description="Récupère une permission par son nom (resource:action).",
)
async def get_permission_by_name(
    name: str,
    repository: IPermissionRepository = Depends(get_permission_repository),
):
    """Récupère une permission par son nom."""
    usecase = GetPermissionUseCase(repository)
    try:
        permission = await usecase.execute(name=name)
        return _to_response_dto(permission)
    except PermissionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================
# Endpoints d'écriture (admin uniquement)
# ============================================

@router.post(
    "",
    response_model=PermissionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une permission",
    description="Crée une nouvelle permission. Réservé aux administrateurs.",
)
async def create_permission(
    dto: CreatePermissionDTO,
    repository: IPermissionRepository = Depends(get_permission_repository),
    _: None = Depends(get_current_superuser),
):
    """Crée une nouvelle permission."""
    usecase = CreatePermissionUseCase(repository)
    try:
        permission = await usecase.execute(dto)
        return _to_response_dto(permission)
    except PermissionAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/bulk",
    response_model=List[PermissionResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Créer plusieurs permissions",
    description="Crée plusieurs permissions en une seule opération. Les doublons sont ignorés.",
)
async def create_bulk_permissions(
    permissions: List[CreatePermissionDTO],
    repository: IPermissionRepository = Depends(get_permission_repository),
    _: None = Depends(get_current_superuser),
):
    """Crée plusieurs permissions."""
    usecase = CreateBulkPermissionsUseCase(repository)
    created = await usecase.execute(permissions)
    return [_to_response_dto(p) for p in created]


@router.patch(
    "/{permission_id}",
    response_model=PermissionResponseDTO,
    summary="Mettre à jour une permission",
    description="Met à jour une permission existante. Réservé aux administrateurs.",
)
async def update_permission(
    permission_id: str,
    dto: UpdatePermissionDTO,
    repository: IPermissionRepository = Depends(get_permission_repository),
    _: None = Depends(get_current_superuser),
):
    """Met à jour une permission."""
    usecase = UpdatePermissionUseCase(repository)
    try:
        permission = await usecase.execute(permission_id, dto)
        return _to_response_dto(permission)
    except PermissionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une permission",
    description="Supprime une permission. Réservé aux administrateurs. "
                "Les permissions système ne peuvent pas être supprimées. "
                "Une permission utilisée par un rôle ne peut pas être supprimée.",
)
async def delete_permission(
    permission_id: str,
    repository: IPermissionRepository = Depends(get_permission_repository),
    role_repository: IRoleRepository = Depends(get_role_repository),
    _: None = Depends(get_current_superuser),
):
    """Supprime une permission."""
    usecase = DeletePermissionUseCase(repository, role_repository)
    try:
        await usecase.execute(permission_id)
    except PermissionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionInUseError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
