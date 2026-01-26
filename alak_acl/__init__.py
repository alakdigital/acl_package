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
__author__ = "ALAK Team"
__license__ = "MIT"

from alak_acl.manager import ACLManager
from alak_acl.shared.config import ACLConfig
from alak_acl.shared.exceptions import (
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
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.domain.dtos.login_dto import LoginDTO
from alak_acl.auth.domain.dtos.register_dto import RegisterDTO
from alak_acl.auth.domain.dtos.token_dto import TokenDTO

# Modèle MongoDB (pas de dépendance SQL)
from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel, create_mongo_user_model
from alak_acl.auth.infrastructure.mappers.auth_user_mapper import AuthUserMapper

# Dépendances FastAPI Auth
from alak_acl.auth.interface.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
)

# Entités et DTOs Roles
from alak_acl.roles.domain.entities.role import Role
from alak_acl.roles.domain.dtos.role_dto import (
    CreateRoleDTO,
    UpdateRoleDTO,
    RoleResponseDTO,
    AssignRoleDTO,
    UserRolesResponseDTO,
)

# Dépendances FastAPI Roles
from alak_acl.roles.interface.dependencies import (
    RequireRole,
    RequireRoles,
    RequirePermission,
    RequirePermissions,
    get_current_user_roles,
    get_current_user_permissions,
)

# Entités et DTOs Permissions
from alak_acl.permissions.domain.entities.permission import Permission
from alak_acl.permissions.domain.dtos.permission_dto import (
    CreatePermissionDTO,
    UpdatePermissionDTO,
    PermissionResponseDTO,
    PermissionListResponseDTO,
)


# Lazy imports pour les modèles SQL (évite de charger SQLAlchemy si non utilisé)
def __getattr__(name: str):
    """Lazy loading des classes SQL pour éviter les dépendances manquantes."""
    # Modèles SQL Auth
    if name == "SQLAuthUserModel":
        from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel
        return SQLAuthUserModel
    elif name == "create_user_model":
        from alak_acl.auth.infrastructure.models.sql_model import create_user_model
        return create_user_model
    # Base SQLAlchemy
    elif name == "Base":
        from alak_acl.shared.database.declarative_base import Base
        return Base
    # Modèles SQL Roles
    elif name == "SQLRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel
        return SQLRoleModel
    elif name == "SQLUserRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLUserRoleModel
        return SQLUserRoleModel
    # Modèles SQL Permissions
    elif name == "SQLPermissionModel":
        from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
        return SQLPermissionModel
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
