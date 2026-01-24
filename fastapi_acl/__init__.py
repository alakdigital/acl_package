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
    PermissionAlreadyExistsError,
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

# Modèles de base extensibles (pour champs personnalisés)
from .auth.infrastructure.models.sql_model import SQLAuthUserModel, create_user_model
from .auth.infrastructure.models.mongo_model import MongoAuthUserModel, create_mongo_user_model
from .auth.infrastructure.mappers.auth_user_mapper import AuthUserMapper

# Dépendances FastAPI Auth
from .auth.interface.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
)

# Entités et DTOs Roles
from .roles.domain.entities.role import Role
from .roles.domain.dtos.role_dto import (
    CreateRoleDTO,
    UpdateRoleDTO,
    RoleResponseDTO,
    AssignRoleDTO,
    UserRolesResponseDTO,
)

# Dépendances FastAPI Roles
from .roles.interface.dependencies import (
    RequireRole,
    RequireRoles,
    RequirePermission,
    RequirePermissions,
    get_current_user_roles,
    get_current_user_permissions,
)

# Entités et DTOs Permissions
from .permissions.domain.entities.permission import Permission
from .permissions.domain.dtos.permission_dto import (
    CreatePermissionDTO,
    UpdatePermissionDTO,
    PermissionResponseDTO,
    PermissionListResponseDTO,
)

# Base SQLAlchemy et modèles pour migrations Alembic
from .shared.database import Base
from .roles.infrastructure.models.sql_model import SQLRoleModel, SQLUserRoleModel
from .permissions.infrastructure.models.sql_model import SQLPermissionModel

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
    "PermissionAlreadyExistsError",
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
    # Modèles extensibles (pour champs personnalisés)
    "SQLAuthUserModel",
    "MongoAuthUserModel",
    "create_user_model",
    "create_mongo_user_model",
    "AuthUserMapper",
    # Dépendances Auth
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    # Entités et DTOs Roles
    "Role",
    "CreateRoleDTO",
    "UpdateRoleDTO",
    "RoleResponseDTO",
    "AssignRoleDTO",
    "UserRolesResponseDTO",
    # Dépendances Roles
    "RequireRole",
    "RequireRoles",
    "RequirePermission",
    "RequirePermissions",
    "get_current_user_roles",
    "get_current_user_permissions",
    # Entités et DTOs Permissions
    "Permission",
    "CreatePermissionDTO",
    "UpdatePermissionDTO",
    "PermissionResponseDTO",
    "PermissionListResponseDTO",
    # Base SQLAlchemy et modèles pour migrations
    "Base",
    "SQLRoleModel",
    "SQLUserRoleModel",
    "SQLPermissionModel",
]
