"""
Feature Permissions - Gestion des permissions.

Cette feature gère les permissions sous forme resource:action.
Supporte les wildcards pour les permissions globales.

Example:
    ```python
    from fastapi import FastAPI
    from alak_acl import ACLManager, ACLConfig
    from alak_acl.permissions import Permission, CreatePermissionDTO

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

# Infrastructure - imports directs uniquement pour le mapper (pas de dépendance externe)
from alak_acl.permissions.infrastructure.mappers.permission_mapper import PermissionMapper

# Interface (Routes et dépendances)
from alak_acl.permissions.interface import (
    router,
    set_permission_dependencies,
    get_permission_repository,
)

# Lazy imports pour les classes qui nécessitent des dépendances externes
def __getattr__(name: str):
    """Lazy loading pour éviter les dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo)
    if name == "MongoPermissionModel":
        from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel
        return MongoPermissionModel
    # Modèles SQL (nécessite SQLAlchemy)
    elif name == "SQLPermissionModel":
        from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
        return SQLPermissionModel
    elif name == "PostgreSQLPermissionRepository":
        from alak_acl.permissions.infrastructure.repositories.postgresql_repository import PostgreSQLPermissionRepository
        return PostgreSQLPermissionRepository
    elif name == "MySQLPermissionRepository":
        from alak_acl.permissions.infrastructure.repositories.mysql_repository import MySQLPermissionRepository
        return MySQLPermissionRepository
    elif name == "MongoDBPermissionRepository":
        from alak_acl.permissions.infrastructure.repositories.mongodb_repository import MongoDBPermissionRepository
        return MongoDBPermissionRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
