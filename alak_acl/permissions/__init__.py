"""
Feature Permissions - Gestion des permissions.

Cette feature gère les permissions sous forme resource:action.
Supporte les wildcards pour les permissions globales.

Example:
    ```python
    from fastapi import FastAPI
    from fastapi_acl import ACLManager, ACLConfig
    from fastapi_acl.permissions import Permission, CreatePermissionDTO

    app = FastAPI()

    config = ACLConfig(
        database_type="postgresql",
        postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
        enable_permissions_feature=True,
    )

    acl = ACLManager(config, app=app)

    # Créer une permission
    perm = Permission(
        resource="posts",
        action="create",
        display_name="Créer des articles",
        category="Content",
    )
    print(perm.name)  # "posts:create"

    # Vérifier une permission
    perm.matches("posts:create")  # True
    ```
"""

# Domain
from alak_acl.permissions.domain import (
    Permission,
    CreatePermissionDTO,
    UpdatePermissionDTO,
    PermissionResponseDTO,
    PermissionListResponseDTO,
    AssignPermissionToRoleDTO,
)

# Application - Interface
from alak_acl.permissions.application.interface.permission_repository import IPermissionRepository

# Application - Use Cases
from alak_acl.permissions.application.usecases import (
    CreatePermissionUseCase,
    UpdatePermissionUseCase,
    DeletePermissionUseCase,
    GetPermissionUseCase,
    ListPermissionsUseCase,
    SearchPermissionsUseCase,
    GetPermissionsByResourceUseCase,
    GetPermissionsByCategoryUseCase,
    CreateBulkPermissionsUseCase,
)

# Infrastructure
from alak_acl.permissions.infrastructure import (
    PostgreSQLPermissionRepository,
    MySQLPermissionRepository,
    MongoDBPermissionRepository,
    SQLPermissionModel,
    MongoPermissionModel,
    PermissionMapper,
)

# Interface (Routes et dépendances)
from alak_acl.permissions.interface import (
    router,
    set_permission_dependencies,
    get_permission_repository,
)

__all__ = [
    # Domain - Entité
    "Permission",
    # Domain - DTOs
    "CreatePermissionDTO",
    "UpdatePermissionDTO",
    "PermissionResponseDTO",
    "PermissionListResponseDTO",
    "AssignPermissionToRoleDTO",
    # Application - Interface
    "IPermissionRepository",
    # Application - Use Cases
    "CreatePermissionUseCase",
    "UpdatePermissionUseCase",
    "DeletePermissionUseCase",
    "GetPermissionUseCase",
    "ListPermissionsUseCase",
    "SearchPermissionsUseCase",
    "GetPermissionsByResourceUseCase",
    "GetPermissionsByCategoryUseCase",
    "CreateBulkPermissionsUseCase",
    # Infrastructure - Repositories
    "PostgreSQLPermissionRepository",
    "MySQLPermissionRepository",
    "MongoDBPermissionRepository",
    # Infrastructure - Modèles
    "SQLPermissionModel",
    "MongoPermissionModel",
    # Infrastructure - Mapper
    "PermissionMapper",
    # Interface - Router
    "router",
    # Interface - Configuration
    "set_permission_dependencies",
    "get_permission_repository",
]
