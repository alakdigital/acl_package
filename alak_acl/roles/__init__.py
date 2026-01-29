"""
Feature Roles - Gestion des rôles et permissions.

Cette feature gère les rôles, leurs associations avec les permissions,
et l'assignation des rôles aux utilisateurs.

Example:
    ```python
    from fastapi import FastAPI, Depends
    from alak_acl import ACLManager, ACLConfig
    from alak_acl.roles import RequireRole, RequirePermission

    app = FastAPI()

    config = ACLConfig(
        database_type="postgresql",
        postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
        enable_roles_feature=True,
    )

    acl = ACLManager(config, app=app)

    @app.get("/admin/dashboard")
    async def admin_dashboard(
        user = Depends(RequireRole("admin"))
    ):
        return {"message": "Bienvenue admin!"}

    @app.post("/posts")
    async def create_post(
        user = Depends(RequirePermission("posts:create"))
    ):
        return {"message": "Post créé!"}
    ```
"""

# Domain
from alak_acl.roles.domain import (
    Role,
    CreateRoleDTO,
    UpdateRoleDTO,
    RoleResponseDTO,
    RoleListResponseDTO,
    AssignRoleDTO,
    AssignRolesDTO,
    UserRolesResponseDTO,
)

# Application - Interface
from alak_acl.roles.application.interface.role_repository import IRoleRepository

# Application - Use Cases
from alak_acl.roles.application.usecases import (
    CreateRoleUseCase,
    UpdateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListRolesUseCase,
    AssignRoleUseCase,
    RemoveRoleUseCase,
    GetUserRolesUseCase,
    GetUserPermissionsUseCase,
    CheckPermissionUseCase,
    CheckRoleUseCase,
    SetUserRolesUseCase,
    AssignDefaultRolesUseCase,
)

# Infrastructure - imports directs uniquement pour le mapper (pas de dépendance externe)
from alak_acl.roles.infrastructure.mappers.role_mapper import RoleMapper


# Lazy imports pour éviter les imports circulaires et les dépendances manquantes
def __getattr__(name: str):
    """Lazy loading pour éviter les imports circulaires et dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo)
    if name == "MongoRoleModel":
        from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel
        return MongoRoleModel
    elif name == "MongoUserRoleModel":
        from alak_acl.roles.infrastructure.models.mongo_model import MongoUserRoleModel
        return MongoUserRoleModel
    # Interface (Routes et dépendances) - lazy pour éviter import circulaire avec auth
    elif name == "router":
        from alak_acl.roles.interface.routes import router
        return router
    elif name == "set_role_dependencies":
        from alak_acl.roles.interface.dependencies import set_role_dependencies
        return set_role_dependencies
    elif name == "get_role_repository":
        from alak_acl.roles.interface.dependencies import get_role_repository
        return get_role_repository
    elif name == "get_current_user_roles":
        from alak_acl.roles.interface.dependencies import get_current_user_roles
        return get_current_user_roles
    elif name == "get_current_user_permissions":
        from alak_acl.roles.interface.dependencies import get_current_user_permissions
        return get_current_user_permissions
    elif name == "RequireRole":
        from alak_acl.roles.interface.dependencies import RequireRole
        return RequireRole
    elif name == "RequireRoles":
        from alak_acl.roles.interface.dependencies import RequireRoles
        return RequireRoles
    elif name == "RequirePermission":
        from alak_acl.roles.interface.dependencies import RequirePermission
        return RequirePermission
    elif name == "RequirePermissions":
        from alak_acl.roles.interface.dependencies import RequirePermissions
        return RequirePermissions
    # Modèles SQL
    elif name == "SQLRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel
        return SQLRoleModel
    elif name == "SQLUserRoleModel":
        from alak_acl.roles.infrastructure.models.sql_model import SQLUserRoleModel
        return SQLUserRoleModel
    # Repositories
    elif name == "PostgreSQLRoleRepository":
        from alak_acl.roles.infrastructure.repositories.postgresql_repository import PostgreSQLRoleRepository
        return PostgreSQLRoleRepository
    elif name == "MySQLRoleRepository":
        from alak_acl.roles.infrastructure.repositories.mysql_repository import MySQLRoleRepository
        return MySQLRoleRepository
    elif name == "MongoDBRoleRepository":
        from alak_acl.roles.infrastructure.repositories.mongodb_repository import MongoDBRoleRepository
        return MongoDBRoleRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Domain - Entité
    "Role",
    # Domain - DTOs
    "CreateRoleDTO",
    "UpdateRoleDTO",
    "RoleResponseDTO",
    "RoleListResponseDTO",
    "AssignRoleDTO",
    "AssignRolesDTO",
    "UserRolesResponseDTO",
    # Application - Interface
    "IRoleRepository",
    # Application - Use Cases
    "CreateRoleUseCase",
    "UpdateRoleUseCase",
    "DeleteRoleUseCase",
    "GetRoleUseCase",
    "ListRolesUseCase",
    "AssignRoleUseCase",
    "RemoveRoleUseCase",
    "GetUserRolesUseCase",
    "GetUserPermissionsUseCase",
    "CheckPermissionUseCase",
    "CheckRoleUseCase",
    "SetUserRolesUseCase",
    "AssignDefaultRolesUseCase",
    # Infrastructure - Repositories
    "PostgreSQLRoleRepository",
    "MySQLRoleRepository",
    "MongoDBRoleRepository",
    # Infrastructure - Modèles
    "SQLRoleModel",
    "SQLUserRoleModel",
    "MongoRoleModel",
    "MongoUserRoleModel",
    # Infrastructure - Mapper
    "RoleMapper",
    # Interface - Router
    "router",
    # Interface - Configuration
    "set_role_dependencies",
    "get_role_repository",
    # Interface - Dépendances
    "get_current_user_roles",
    "get_current_user_permissions",
    "RequireRole",
    "RequireRoles",
    "RequirePermission",
    "RequirePermissions",
]
