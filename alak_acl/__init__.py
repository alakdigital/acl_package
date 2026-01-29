"""
fastapi-acl - Package de gestion ACL pour FastAPI.

Package professionnel pour gérer l'authentification et les permissions
(ACL - Access Control List) dans des applications FastAPI.

Example:
    ```python
    from fastapi import FastAPI
    from alak_acl import ACLManager, ACLConfig

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

from typing import TYPE_CHECKING

__version__ = "0.1.0"
__author__ = "ALAK Team"
__license__ = "MIT"

# Type hints pour l'autocomplétion IDE (non exécuté à runtime)
if TYPE_CHECKING:
    from alak_acl.shared.database.declarative_base import Base as Base
    from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel as SQLAuthUserModel
    from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel as MongoAuthUserModel
    from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel as SQLRoleModel
    from alak_acl.roles.infrastructure.models.sql_model import SQLUserRoleModel as SQLUserRoleModel
    from alak_acl.roles.infrastructure.models.sql_model import SQLMembershipModel as SQLMembershipModel
    from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel as SQLPermissionModel

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
    ResetTokenExpiredError,
    ResetTokenInvalidError,
    EmailSendError,
)

# Entités et DTOs Auth
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.domain.dtos.login_dto import LoginDTO
from alak_acl.auth.domain.dtos.register_dto import RegisterDTO
from alak_acl.auth.domain.dtos.token_dto import TokenDTO
from alak_acl.auth.domain.dtos.password_reset_dto import ForgotPasswordDTO, ResetPasswordDTO

# Mapper Auth (pas de dépendance externe)
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


# Lazy imports pour les modèles (évite de charger les dépendances non installées)
def __getattr__(name: str):
    """Lazy loading des classes pour éviter les dépendances manquantes."""
    # Modèles MongoDB Auth (nécessite motor/pymongo)
    if name == "MongoAuthUserModel":
        from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel
        return MongoAuthUserModel
    # Modèles SQL Auth (nécessite SQLAlchemy)
    elif name == "SQLAuthUserModel":
        from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel
        return SQLAuthUserModel
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
    elif name == "SQLMembershipModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLMembershipModel
        return SQLMembershipModel
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
    "ResetTokenExpiredError",
    "ResetTokenInvalidError",
    "EmailSendError",
    # Entités et DTOs
    "AuthUser",
    "LoginDTO",
    "RegisterDTO",
    "TokenDTO",
    "ForgotPasswordDTO",
    "ResetPasswordDTO",
    # Modèles extensibles (pour champs personnalisés)
    "SQLAuthUserModel",
    "MongoAuthUserModel",
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
    "SQLMembershipModel",
    "SQLPermissionModel",
]
