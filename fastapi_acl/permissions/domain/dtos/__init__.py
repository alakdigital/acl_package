"""
DTOs du domaine Permissions.
"""

from .permission_dto import (
    CreatePermissionDTO,
    UpdatePermissionDTO,
    PermissionResponseDTO,
    PermissionListResponseDTO,
    AssignPermissionToRoleDTO,
)

__all__ = [
    "CreatePermissionDTO",
    "UpdatePermissionDTO",
    "PermissionResponseDTO",
    "PermissionListResponseDTO",
    "AssignPermissionToRoleDTO",
]
