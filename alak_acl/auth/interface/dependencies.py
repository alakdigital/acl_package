"""
Dépendances FastAPI pour l'authentification.
"""

from typing import Optional, TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.application.interface.token_service import ITokenService
from alak_acl.auth.application.interface.password_hasher import IPasswordHasher
from alak_acl.auth.application.usecases.login_usecase import LoginUseCase
from alak_acl.auth.application.usecases.register_usecase import RegisterUseCase
from alak_acl.auth.application.usecases.refresh_token_usecase import RefreshTokenUseCase
from alak_acl.auth.application.usecases.forgot_password_usecase import ForgotPasswordUseCase
from alak_acl.auth.application.usecases.reset_password_usecase import ResetPasswordUseCase
from alak_acl.auth.application.interface.email_service import IEmailService
from alak_acl.shared.config import ACLConfig
from alak_acl.shared.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
)
from alak_acl.shared.logging import logger

if TYPE_CHECKING:
    from alak_acl.roles.application.interface.role_repository import IRoleRepository


# Security scheme pour Swagger
security = HTTPBearer(auto_error=False)


# Variables globales pour les instances (initialisées par ACLManager)
_auth_repository: Optional[IAuthRepository] = None
_token_service: Optional[ITokenService] = None
_password_hasher: Optional[IPasswordHasher] = None
_role_repository: Optional["IRoleRepository"] = None
_email_service: Optional[IEmailService] = None
_reset_url_base: Optional[str] = None
_config: Optional[ACLConfig] = None


def set_auth_dependencies(
    auth_repository: IAuthRepository,
    token_service: ITokenService,
    password_hasher: IPasswordHasher,
    role_repository: Optional["IRoleRepository"] = None,
    config: Optional[ACLConfig] = None,
) -> None:
    """
    Configure les dépendances d'authentification.

    Appelé par ACLManager lors de l'initialisation.

    Args:
        auth_repository: Repository d'authentification
        token_service: Service de tokens
        password_hasher: Service de hashage
        role_repository: Repository des rôles (optionnel)
        config: Configuration ACL (optionnel)
    """
    global _auth_repository, _token_service, _password_hasher, _role_repository, _config
    _auth_repository = auth_repository
    _token_service = token_service
    _password_hasher = password_hasher
    _role_repository = role_repository
    _config = config


def set_email_dependencies(
    email_service: Optional[IEmailService] = None,
    reset_url_base: Optional[str] = None,
) -> None:
    """
    Configure les dépendances email pour le reset de mot de passe.

    Appelé par ACLManager lors de l'initialisation.

    Args:
        email_service: Service d'email (SMTP ou Console)
        reset_url_base: URL de base pour les liens de reset
    """
    global _email_service, _reset_url_base
    _email_service = email_service
    _reset_url_base = reset_url_base


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


def get_role_repository() -> Optional["IRoleRepository"]:
    """
    Récupère le repository des rôles.

    Returns:
        Repository des rôles ou None si non configuré
    """
    return _role_repository


def get_email_service() -> Optional[IEmailService]:
    """
    Récupère le service d'email.

    Returns:
        Service d'email ou None si non configuré
    """
    return _email_service

def get_config() -> ACLConfig:
    """
    Récupère la configuration ACL.

    Returns:
        Configuration ACL

    Raises:
        HTTPException: Si non initialisé
    """
    if _config is None:
        # Retourner une config par défaut si non initialisée
        return ACLConfig()
    return _config


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
        raise e

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


def get_forgot_password_usecase(
    auth_repository: IAuthRepository = Depends(get_auth_repository),
    token_service: ITokenService = Depends(get_token_service),
    email_service: Optional[IEmailService] = Depends(get_email_service),
) -> ForgotPasswordUseCase:
    """
    Instancie le use case de demande de réinitialisation de mot de passe.

    Returns:
        Instance de ForgotPasswordUseCase
    """
    from alak_acl.auth.infrastructure.services.console_email_service import ConsoleEmailService

    # Utiliser ConsoleEmailService si aucun service email n'est configuré
    effective_email_service = email_service or ConsoleEmailService()

    return ForgotPasswordUseCase(
        auth_repository=auth_repository,
        token_service=token_service,
        email_service=effective_email_service,
        reset_url_base=_reset_url_base,
    )


def get_reset_password_usecase(
    auth_repository: IAuthRepository = Depends(get_auth_repository),
    token_service: ITokenService = Depends(get_token_service),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> ResetPasswordUseCase:
    """
    Instancie le use case de réinitialisation de mot de passe.

    Returns:
        Instance de ResetPasswordUseCase
    """
    return ResetPasswordUseCase(
        auth_repository=auth_repository,
        token_service=token_service,
        password_hasher=password_hasher,
    )
