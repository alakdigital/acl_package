"""
Use cases pour la feature Permissions.
"""

from .permission_usecases import (
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

__all__ = [
    "CreatePermissionUseCase",
    "UpdatePermissionUseCase",
    "DeletePermissionUseCase",
    "GetPermissionUseCase",
    "ListPermissionsUseCase",
    "SearchPermissionsUseCase",
    "GetPermissionsByResourceUseCase",
    "GetPermissionsByCategoryUseCase",
    "CreateBulkPermissionsUseCase",
]
