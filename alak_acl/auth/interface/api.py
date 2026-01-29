"""
Routes publiques de l'API d'authentification.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from alak_acl.auth.domain.dtos.login_dto import LoginDTO
from alak_acl.auth.domain.dtos.register_dto import RegisterDTO
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.application.usecases.login_usecase import LoginUseCase
from alak_acl.auth.application.usecases.register_usecase import RegisterUseCase
from alak_acl.auth.application.usecases.refresh_token_usecase import RefreshTokenUseCase
from alak_acl.auth.application.usecases.forgot_password_usecase import ForgotPasswordUseCase
from alak_acl.auth.application.usecases.reset_password_usecase import ResetPasswordUseCase
from alak_acl.auth.domain.dtos.password_reset_dto import ForgotPasswordDTO, ResetPasswordDTO
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
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from alak_acl.auth.interface.dependencies import (
    get_login_usecase,
    get_register_usecase,
    get_refresh_token_usecase,
    get_forgot_password_usecase,
    get_reset_password_usecase,
    get_current_active_user,
    get_role_repository,
    get_config,
)
from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.shared.config import ACLConfig
from alak_acl.shared.cache.utils import CachePrefix, get_user_cache, invalidate_all_user_caches, set_user_cache
from alak_acl.shared.exceptions import (
    ACLException,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotActiveError,
    InvalidTokenError,
    ResetTokenExpiredError,
    ResetTokenInvalidError,
)
from alak_acl.shared.logging import logger


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouvel utilisateur",
    description=(
        "Crée un nouveau compte utilisateur. "
        "Cette route est désactivée par défaut en mode SaaS. "
        "Utilisez enable_public_registration=True pour l'activer."
    ),
)
async def register(
    request: RegisterRequest,
    register_usecase: RegisterUseCase = Depends(get_register_usecase),
    config: ACLConfig = Depends(get_config),
) -> UserResponse:
    """
    Inscrit un nouvel utilisateur.

    Note SaaS:
        En mode SaaS, cette route est désactivée par défaut.
        L'application hôte doit créer les comptes via ACLManager.create_account()
        puis assigner les utilisateurs aux tenants via ACLManager.assign_role().

    Args:
        request: Données d'inscription
        register_usecase: Use case d'inscription
        config: Configuration ACL

    Returns:
        Informations de l'utilisateur créé

    Raises:
        HTTPException 403: Si l'inscription publique est désactivée
    """
    # Vérifier si l'inscription publique est activée
    if not config.enable_public_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "L'inscription publique est désactivée. "
                "Contactez l'administrateur pour créer un compte."
            ),
        )

    try:
        register_dto = RegisterDTO(
            username=request.username,
            email=request.email,
            password=request.password,
        )
        user = await register_usecase.execute(register_dto)

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

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserAlreadyExistsError as e:
        raise e


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
        raise e


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
        raise e
    except ACLException as e:
        raise e


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Informations utilisateur connecté",
    description=(
        "Retourne les informations de l'utilisateur authentifié avec ses rôles et permissions. "
        "Les rôles globaux (sans tenant) sont toujours inclus. "
        "En mode SaaS, spécifiez le header X-Tenant-ID pour inclure également les rôles du tenant."
    ),
)
async def get_me(
    current_user: AuthUser = Depends(get_current_active_user),
    role_repository: IRoleRepository = Depends(get_role_repository),
    config: ACLConfig = Depends(get_config),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> UserMeResponse:
    """
    Récupère les informations de l'utilisateur connecté avec ses rôles et permissions.

    Comportement:
    - Les rôles globaux (tenant_id=NULL) sont toujours retournés
    - Si X-Tenant-ID est spécifié, les rôles de ce tenant sont aussi inclus
    - La liste 'tenants' contient tous les tenants de l'utilisateur

    Args:
        current_user: Utilisateur authentifié
        role_repository: Repository des rôles
        config: Configuration ACL
        x_tenant_id: ID du tenant (header optionnel, pour inclure les rôles du tenant)

    Returns:
        Informations utilisateur avec rôles et permissions
    """
    # Vérifier le cache si activé
    if config.enable_cache:
        cached_data = await get_user_cache(
            user_id=current_user.id,
            tenant_id=x_tenant_id,
            prefix=CachePrefix.USER_ME,
        )
        if cached_data:
            return UserMeResponse(**cached_data)

    # Cache MISS - Récupérer les données
    roles_response = []
    all_permissions = set()
    user_tenants = []

    if role_repository:
        try:
            # Récupérer la liste des tenants de l'utilisateur
            user_tenants = await role_repository.get_user_tenants(current_user.id)

            # Toujours récupérer les rôles globaux (tenant_id=NULL)
            global_roles = await role_repository.get_user_roles(current_user.id, None)
            for role in global_roles:
                if role.is_active:
                    roles_response.append(RoleResponse(
                        id=role.id,
                        name=role.name,
                        display_name=role.display_name,
                        permissions=role.permissions or [],
                        tenant_id=None,
                    ))
                    all_permissions.update(role.permissions or [])

            # Si un tenant est spécifié, récupérer aussi les rôles de ce tenant
            if x_tenant_id:
                tenant_roles = await role_repository.get_user_roles(current_user.id, x_tenant_id)
                for role in tenant_roles:
                    if role.is_active:
                        roles_response.append(RoleResponse(
                            id=role.id,
                            name=role.name,
                            display_name=role.display_name,
                            permissions=role.permissions or [],
                            tenant_id=role.tenant_id,
                        ))
                        all_permissions.update(role.permissions or [])
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des rôles: {e}")

    response = UserMeResponse(
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
        tenants=user_tenants,
    )

    # Stocker en cache si activé
    if config.enable_cache:
        await set_user_cache(
            user_id=current_user.id,
            data=response,
            tenant_id=x_tenant_id,
            prefix=CachePrefix.USER_ME,
            ttl=config.cache_ttl,
        )

    return response


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
    await invalidate_all_user_caches(current_user.id)
    return MessageResponse(
        message="Déconnexion réussie",
        success=True,
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Demande de réinitialisation de mot de passe",
    description="Envoie un email avec un lien de réinitialisation si l'adresse existe.",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    forgot_password_usecase: ForgotPasswordUseCase = Depends(get_forgot_password_usecase),
) -> MessageResponse:
    """
    Demande la réinitialisation du mot de passe.

    Pour des raisons de sécurité, retourne toujours un succès même si
    l'email n'existe pas (évite l'énumération des utilisateurs).

    Args:
        request: Email de l'utilisateur
        forgot_password_usecase: Use case de demande de reset

    Returns:
        Message de confirmation
    """
    try:
        dto = ForgotPasswordDTO(email=request.email)
        await forgot_password_usecase.execute(dto)

        return MessageResponse(
            message="Si cette adresse email est associée à un compte, "
                    "vous recevrez un email avec les instructions de réinitialisation.",
            success=True,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Réinitialisation du mot de passe",
    description="Réinitialise le mot de passe avec le token reçu par email.",
)
async def reset_password(
    request: ResetPasswordRequest,
    reset_password_usecase: ResetPasswordUseCase = Depends(get_reset_password_usecase),
) -> MessageResponse:
    """
    Réinitialise le mot de passe avec un token valide.

    Args:
        request: Token et nouveau mot de passe
        reset_password_usecase: Use case de réinitialisation

    Returns:
        Message de confirmation
    """
    try:
        dto = ResetPasswordDTO(
            token=request.token,
            new_password=request.new_password,
        )
        await reset_password_usecase.execute(dto)

        return MessageResponse(
            message="Votre mot de passe a été réinitialisé avec succès.",
            success=True,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except (ResetTokenExpiredError, ResetTokenInvalidError) as e:
        raise e
    except ACLException as e:
        raise e
