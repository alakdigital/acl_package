"""
fastapi-acl - Package de gestion ACL pour FastAPI.

Package professionnel pour gérer l'authentification et les permissions
(ACL - Access Control List) dans des applications FastAPI.

Example:
    ```python
    from fastapi import FastAPI
    from fastapi_acl import ACLManager, ACLConfig

    app = FastAPI()

    config = ACLConfig(
        database_type="postgresql",
        postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
        enable_cache=True,
        redis_url="redis://localhost:6379/0",
        enable_auth_feature=True,
        enable_api_routes=True,
    )

    acl = ACLManager(config, app=app)

    @app.on_event("startup")
    async def startup():
        await acl.initialize()

    @app.on_event("shutdown")
    async def shutdown():
        await acl.close()

    # Les routes sont automatiquement enregistrées dans Swagger !
    ```
"""

__version__ = "0.1.0"
__author__ = "FastAPI ACL Team"
__license__ = "MIT"

from .manager import ACLManager
from .shared.config import ACLConfig
from .shared.exceptions import (
    ACLException,
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserNotFoundError,
    UserNotActiveError,
    UserAlreadyExistsError,
    UserNotVerifiedError,
    PermissionDeniedError,
    PermissionNotFoundError,
    RoleNotFoundError,
    RoleAlreadyExistsError,
    DatabaseConnectionError,
    CacheConnectionError,
    ConfigurationError,
)

# Entités et DTOs Auth
from .auth.domain.entities.auth_user import AuthUser
from .auth.domain.dtos.login_dto import LoginDTO
from .auth.domain.dtos.register_dto import RegisterDTO
from .auth.domain.dtos.token_dto import TokenDTO

# Dépendances FastAPI
from .auth.interface.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
)

__all__ = [
    # Version
    "__version__",
    # Manager principal
    "ACLManager",
    "ACLConfig",
    # Exceptions
    "ACLException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "TokenExpiredError",
    "UserNotFoundError",
    "UserNotActiveError",
    "UserAlreadyExistsError",
    "UserNotVerifiedError",
    "PermissionDeniedError",
    "PermissionNotFoundError",
    "RoleNotFoundError",
    "RoleAlreadyExistsError",
    "DatabaseConnectionError",
    "CacheConnectionError",
    "ConfigurationError",
    # Entités et DTOs
    "AuthUser",
    "LoginDTO",
    "RegisterDTO",
    "TokenDTO",
    # Dépendances
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
]
