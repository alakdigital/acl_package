"""
Routes publiques de l'API d'authentification.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from alak_acl.auth.domain.dtos.login_dto import LoginDTO
from alak_acl.auth.domain.dtos.register_dto import RegisterDTO
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.application.usecases.login_usecase import LoginUseCase
from alak_acl.auth.application.usecases.register_usecase import RegisterUseCase
from alak_acl.auth.application.usecases.refresh_token_usecase import RefreshTokenUseCase
from alak_acl.auth.interface.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    UserMeResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    MessageResponse,
    RoleResponse,
)
from alak_acl.auth.interface.dependencies import (
    get_login_usecase,
    get_register_usecase,
    get_refresh_token_usecase,
    get_current_active_user,
    get_role_repository,
)
from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.shared.exceptions import (
    ACLException,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotActiveError,
    InvalidTokenError,
)
from alak_acl.shared.logging import logger


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouvel utilisateur",
    description="Crée un nouveau compte utilisateur.",
)
async def register(
    request: RegisterRequest,
    register_usecase: RegisterUseCase = Depends(get_register_usecase),
) -> UserResponse:
    """
    Inscrit un nouvel utilisateur.

    Args:
        request: Données d'inscription
        register_usecase: Use case d'inscription

    Returns:
        Informations de l'utilisateur créé
    """
    try:
        register_dto = RegisterDTO(
            username=request.username,
            email=request.email,
            password=request.password,
            tenant_id=request.tenant_id,
        )
        user = await register_usecase.execute(register_dto)

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            tenant_id=user.tenant_id,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Connexion utilisateur",
    description="Authentifie un utilisateur et retourne les tokens JWT.",
)
async def login(
    request: LoginRequest,
    login_usecase: LoginUseCase = Depends(get_login_usecase),
) -> LoginResponse:
    """
    Connecte un utilisateur.

    Args:
        request: Données de connexion
        login_usecase: Use case de connexion

    Returns:
        Tokens d'authentification
    """
    try:
        login_dto = LoginDTO(
            username=request.username,
            password=request.password,
        )
        token_dto = await login_usecase.execute(login_dto)

        return LoginResponse(
            access_token=token_dto.access_token,
            refresh_token=token_dto.refresh_token,
            token_type=token_dto.token_type,
            expires_in=token_dto.expires_in or 1800,
        )

    except (InvalidCredentialsError, UserNotActiveError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Rafraîchir le token",
    description="Obtient un nouveau token d'accès avec le refresh token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    refresh_usecase: RefreshTokenUseCase = Depends(get_refresh_token_usecase),
) -> RefreshTokenResponse:
    """
    Rafraîchit le token d'accès.

    Args:
        request: Refresh token
        refresh_usecase: Use case de rafraîchissement

    Returns:
        Nouveau token d'accès
    """
    try:
        token_dto = await refresh_usecase.execute(request.refresh_token)

        return RefreshTokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
            expires_in=token_dto.expires_in or 1800,
        )

    except (InvalidTokenError, UserNotActiveError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ACLException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Informations utilisateur connecté",
    description="Retourne les informations de l'utilisateur authentifié avec ses rôles et permissions.",
)
async def get_me(
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> UserMeResponse:
    """
    Récupère les informations de l'utilisateur connecté avec ses rôles et permissions.

    Args:
        current_user: Utilisateur authentifié
        role_repository: Repository des rôles

    Returns:
        Informations utilisateur avec rôles et permissions
    """
    roles_response = []
    all_permissions = set()

    if role_repository:
        try:
            roles = await role_repository.get_user_roles(current_user.id)
            for role in roles:
                if role.is_active:
                    roles_response.append(RoleResponse(
                        id=role.id,
                        name=role.name,
                        display_name=role.display_name,
                        permissions=role.permissions or [],
                    ))
                    all_permissions.update(role.permissions or [])
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des rôles: {e}")

    return UserMeResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        roles=roles_response,
        permissions=sorted(list(all_permissions)),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Déconnexion",
    description="Déconnecte l'utilisateur (côté client uniquement).",
)
async def logout(
    current_user: AuthUser = Depends(get_current_active_user),
) -> MessageResponse:
    """
    Déconnecte l'utilisateur.

    Note: Avec JWT stateless, la déconnexion est gérée côté client
    en supprimant le token. Cette route sert principalement
    à confirmer la déconnexion.

    Args:
        current_user: Utilisateur authentifié

    Returns:
        Message de confirmation
    """
    logger.info(f"Déconnexion de l'utilisateur: {current_user.username}")

    return MessageResponse(
        message="Déconnexion réussie",
        success=True,
    )
