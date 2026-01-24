"""
Feature Roles - Gestion des rôles et permissions.

Cette feature gère les rôles, leurs associations avec les permissions,
et l'assignation des rôles aux utilisateurs.

Example:
    ```python
    from fastapi import FastAPI, Depends
    from fastapi_acl import ACLManager, ACLConfig
    from fastapi_acl.roles import RequireRole, RequirePermission

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

# Infrastructure
from alak_acl.roles.infrastructure import (
    PostgreSQLRoleRepository,
    MySQLRoleRepository,
    MongoDBRoleRepository,
    SQLRoleModel,
    SQLUserRoleModel,
    MongoRoleModel,
    MongoUserRoleModel,
    RoleMapper,
)

# Interface (Routes et dépendances)
from alak_acl.roles.interface import (
    router,
    set_role_dependencies,
    get_role_repository,
    get_current_user_roles,
    get_current_user_permissions,
    RequireRole,
    RequireRoles,
    RequirePermission,
    RequirePermissions,
)

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
