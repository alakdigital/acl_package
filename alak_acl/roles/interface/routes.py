"""
Routes API pour la feature Roles.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.interface.dependencies import get_current_active_user
from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.roles.application.usecases.role_usecases import (
    CreateRoleUseCase,
    UpdateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListRolesUseCase,
    AssignRoleUseCase,
    RemoveRoleUseCase,
    GetUserRolesUseCase,
    GetUserPermissionsUseCase,
)
from alak_acl.roles.domain.dtos.role_dto import (
    CreateRoleDTO,
    UpdateRoleDTO,
    RoleResponseDTO,
    RoleListResponseDTO,
    AssignRoleDTO,
    UserRolesResponseDTO,
    AddPermissionDTO,
)
from alak_acl.roles.domain.entities.role import Role
from alak_acl.roles.interface.dependencies import RequirePermission, get_role_repository
from alak_acl.shared.exceptions import PermissionDeniedError, RoleAlreadyExistsError, RoleNotFoundError


router = APIRouter(prefix="/roles", tags=["roles"])


def role_to_response(role: Role) -> RoleResponseDTO:
    """Convertit une entité Role en DTO de réponse."""
    return RoleResponseDTO(
        id=role.id,
        name=role.name,
        display_name=role.display_name or role.name,
        description=role.description,
        permissions=role.permissions,
        is_active=role.is_active,
        is_default=role.is_default,
        is_system=role.is_system,
        priority=role.priority,
        tenant_id=role.tenant_id,
        created_at=role.created_at,
        updated_at=role.updated_at,
    )


# ==========================================
# Routes CRUD pour les rôles
# ==========================================

@router.post(
    "",
    response_model=RoleResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un rôle",
    description="Crée un nouveau rôle. Nécessite le rôle admin ou la permission roles:create.",
)
async def create_role(
    dto: CreateRoleDTO,
    current_user: AuthUser = Depends(RequirePermission("roles:create")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Crée un nouveau rôle."""
    try:
        use_case = CreateRoleUseCase(role_repository)
        role = await use_case.execute(dto)
        return role_to_response(role)
    except RoleAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "",
    response_model=RoleListResponseDTO,
    summary="Lister les rôles",
    description="Liste tous les rôles avec pagination.",
)
async def list_roles(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Limite"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Liste les rôles."""
    use_case = ListRolesUseCase(role_repository)
    roles, total = await use_case.execute(skip=skip, limit=limit, is_active=is_active)

    return RoleListResponseDTO(
        items=[role_to_response(role) for role in roles],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{role_id}",
    response_model=RoleResponseDTO,
    summary="Récupérer un rôle",
    description="Récupère un rôle par son ID.",
)
async def get_role(
    role_id: str,
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Récupère un rôle par son ID."""
    use_case = GetRoleUseCase(role_repository)
    role = await use_case.execute_by_id(role_id)

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rôle non trouvé: {role_id}",
        )

    return role_to_response(role)


@router.get(
    "/name/{name}",
    response_model=RoleResponseDTO,
    summary="Récupérer un rôle par nom",
    description="Récupère un rôle par son nom.",
)
async def get_role_by_name(
    name: str,
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Récupère un rôle par son nom."""
    use_case = GetRoleUseCase(role_repository)
    role = await use_case.execute_by_name(name)

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rôle non trouvé: {name}",
        )

    return role_to_response(role)


@router.patch(
    "/{role_id}",
    response_model=RoleResponseDTO,
    summary="Mettre à jour un rôle",
    description="Met à jour un rôle existant.",
)
async def update_role(
    role_id: str,
    dto: UpdateRoleDTO,
    current_user: AuthUser = Depends(RequirePermission("roles:update")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Met à jour un rôle."""
    try:
        use_case = UpdateRoleUseCase(role_repository)
        role = await use_case.execute(role_id, dto)
        return role_to_response(role)
    except RoleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un rôle",
    description="Supprime un rôle (sauf les rôles système).",
)
async def delete_role(
    role_id: str,
    current_user: AuthUser = Depends(RequirePermission("roles:delete")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Supprime un rôle."""
    try:
        use_case = DeleteRoleUseCase(role_repository)
        deleted = await use_case.execute(role_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rôle non trouvé: {role_id}",
            )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ==========================================
# Routes pour les permissions des rôles
# ==========================================

@router.post(
    "/{role_id}/permissions",
    response_model=RoleResponseDTO,
    summary="Ajouter une permission",
    description="Ajoute une permission à un rôle.",
)
async def add_permission_to_role(
    role_id: str,
    dto: AddPermissionDTO,
    current_user: AuthUser = Depends(RequirePermission("roles:update")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Ajoute une permission à un rôle."""
    role = await role_repository.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rôle non trouvé: {role_id}",
        )

    role.add_permission(dto.permission)
    updated_role = await role_repository.update_role(role)
    return role_to_response(updated_role)


@router.delete(
    "/{role_id}/permissions/{permission}",
    response_model=RoleResponseDTO,
    summary="Retirer une permission",
    description="Retire une permission d'un rôle.",
)
async def remove_permission_from_role(
    role_id: str,
    permission: str,
    current_user: AuthUser = Depends(RequirePermission("roles:update")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Retire une permission d'un rôle."""
    role = await role_repository.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rôle non trouvé: {role_id}",
        )

    role.remove_permission(permission)
    updated_role = await role_repository.update_role(role)
    return role_to_response(updated_role)


# ==========================================
# Routes pour l'assignation des rôles
# ==========================================

@router.post(
    "/assign",
    status_code=status.HTTP_200_OK,
    summary="Assigner un rôle",
    description="Assigne un rôle à un utilisateur.",
)
async def assign_role_to_user(
    dto: AssignRoleDTO,
    current_user: AuthUser = Depends(RequirePermission("roles:assign")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Assigne un rôle à un utilisateur."""
    try:
        use_case = AssignRoleUseCase(role_repository)
        await use_case.execute(dto.user_id, dto.role_id)
        return {"message": "Rôle assigné avec succès"}
    except RoleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_200_OK,
    summary="Retirer un rôle",
    description="Retire un rôle d'un utilisateur.",
)
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    current_user: AuthUser = Depends(RequirePermission("roles:assign")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Retire un rôle d'un utilisateur."""
    use_case = RemoveRoleUseCase(role_repository)
    removed = await use_case.execute(user_id, role_id)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Association rôle-utilisateur non trouvée",
        )

    return {"message": "Rôle retiré avec succès"}


@router.get(
    "/users/{user_id}",
    response_model=UserRolesResponseDTO,
    summary="Rôles d'un utilisateur",
    description="Récupère les rôles et permissions d'un utilisateur.",
)
async def get_user_roles(
    user_id: str,
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Récupère les rôles d'un utilisateur."""
    # Vérifier les permissions (peut voir ses propres rôles ou avoir la permission)
    if user_id != current_user.id and not current_user.is_superuser:
        # Vérifier la permission roles:read
        permissions = await role_repository.get_user_permissions(current_user.id)
        if "roles:read" not in permissions and "*" not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission insuffisante",
            )

    roles = await role_repository.get_user_roles(user_id)
    all_permissions = await role_repository.get_user_permissions(user_id)

    return UserRolesResponseDTO(
        user_id=user_id,
        roles=[role_to_response(role) for role in roles],
        all_permissions=all_permissions,
    )


@router.get(
    "/me",
    response_model=UserRolesResponseDTO,
    summary="Mes rôles",
    description="Récupère les rôles et permissions de l'utilisateur courant.",
)
async def get_my_roles(
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Récupère les rôles de l'utilisateur courant."""
    roles = await role_repository.get_user_roles(current_user.id)
    all_permissions = await role_repository.get_user_permissions(current_user.id)

    return UserRolesResponseDTO(
        user_id=current_user.id,
        roles=[role_to_response(role) for role in roles],
        all_permissions=all_permissions,
    )


@router.get(
    "/{role_id}/users",
    response_model=List[str],
    summary="Utilisateurs d'un rôle",
    description="Récupère les IDs des utilisateurs ayant un rôle.",
)
async def get_role_users(
    role_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: AuthUser = Depends(RequirePermission("roles:read")),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Récupère les utilisateurs ayant un rôle."""
    return await role_repository.get_users_with_role(role_id, skip=skip, limit=limit)
