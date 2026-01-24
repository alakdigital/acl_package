"""
Dépendances FastAPI pour l'authentification.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.application.interface.token_service import ITokenService
from alak_acl.auth.application.interface.password_hasher import IPasswordHasher
from alak_acl.auth.application.usecases.login_usecase import LoginUseCase
from alak_acl.auth.application.usecases.register_usecase import RegisterUseCase
from alak_acl.auth.application.usecases.refresh_token_usecase import RefreshTokenUseCase
from alak_acl.shared.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
)
from alak_acl.shared.logging import logger


# Security scheme pour Swagger
security = HTTPBearer(auto_error=False)


# Variables globales pour les instances (initialisées par ACLManager)
_auth_repository: Optional[IAuthRepository] = None
_token_service: Optional[ITokenService] = None
_password_hasher: Optional[IPasswordHasher] = None


def set_auth_dependencies(
    auth_repository: IAuthRepository,
    token_service: ITokenService,
    password_hasher: IPasswordHasher,
) -> None:
    """
    Configure les dépendances d'authentification.

    Appelé par ACLManager lors de l'initialisation.

    Args:
        auth_repository: Repository d'authentification
        token_service: Service de tokens
        password_hasher: Service de hashage
    """
    global _auth_repository, _token_service, _password_hasher
    _auth_repository = auth_repository
    _token_service = token_service
    _password_hasher = password_hasher


def get_auth_repository() -> IAuthRepository:
    """
    Récupère le repository d'authentification.

    Returns:
        Repository d'authentification

    Raises:
        HTTPException: Si non initialisé
    """
    if _auth_repository is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service d'authentification non initialisé",
        )
    return _auth_repository


def get_token_service() -> ITokenService:
    """
    Récupère le service de tokens.

    Returns:
        Service de tokens

    Raises:
        HTTPException: Si non initialisé
    """
    if _token_service is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service de tokens non initialisé",
        )
    return _token_service


def get_password_hasher() -> IPasswordHasher:
    """
    Récupère le service de hashage.

    Returns:
        Service de hashage

    Raises:
        HTTPException: Si non initialisé
    """
    if _password_hasher is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service de hashage non initialisé",
        )
    return _password_hasher


def get_login_usecase(
    auth_repository: IAuthRepository = Depends(get_auth_repository),
    token_service: ITokenService = Depends(get_token_service),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> LoginUseCase:
    """
    Instancie le use case de connexion.

    Returns:
        Instance de LoginUseCase
    """
    return LoginUseCase(
        auth_repository=auth_repository,
        token_service=token_service,
        password_hasher=password_hasher,
    )


def get_register_usecase(
    auth_repository: IAuthRepository = Depends(get_auth_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> RegisterUseCase:
    """
    Instancie le use case d'inscription.

    Returns:
        Instance de RegisterUseCase
    """
    return RegisterUseCase(
        auth_repository=auth_repository,
        password_hasher=password_hasher,
    )


def get_refresh_token_usecase(
    auth_repository: IAuthRepository = Depends(get_auth_repository),
    token_service: ITokenService = Depends(get_token_service),
) -> RefreshTokenUseCase:
    """
    Instancie le use case de rafraîchissement de token.

    Returns:
        Instance de RefreshTokenUseCase
    """
    return RefreshTokenUseCase(
        auth_repository=auth_repository,
        token_service=token_service,
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_repository: IAuthRepository = Depends(get_auth_repository),
    token_service: ITokenService = Depends(get_token_service),
) -> AuthUser:
    """
    Récupère l'utilisateur courant depuis le token JWT.

    Args:
        credentials: Credentials HTTP Bearer
        auth_repository: Repository d'authentification
        token_service: Service de tokens

    Returns:
        Entité AuthUser de l'utilisateur connecté

    Raises:
        HTTPException 401: Si le token est invalide ou manquant
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification requis",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        user_id = token_service.get_user_id_from_token(token)
    except (InvalidTokenError, TokenExpiredError) as e:
        logger.warning(f"Token invalide: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: AuthUser = Depends(get_current_user),
) -> AuthUser:
    """
    Récupère l'utilisateur courant s'il est actif.

    Args:
        current_user: Utilisateur courant

    Returns:
        Utilisateur actif

    Raises:
        HTTPException 403: Si le compte est désactivé
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte utilisateur désactivé",
        )
    return current_user


async def get_current_superuser(
    current_user: AuthUser = Depends(get_current_active_user),
) -> AuthUser:
    """
    Récupère l'utilisateur courant s'il est superuser.

    Args:
        current_user: Utilisateur courant actif

    Returns:
        Utilisateur superuser

    Raises:
        HTTPException 403: Si l'utilisateur n'est pas superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis",
        )
    return current_user
