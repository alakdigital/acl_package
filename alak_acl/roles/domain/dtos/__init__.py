"""
DTOs pour la feature Roles.
"""

from alak_acl.roles.domain.dtos.role_dto import (
    CreateRoleDTO,
    UpdateRoleDTO,
    RoleResponseDTO,
    RoleListResponseDTO,
    AssignRoleDTO,
    AssignRolesDTO,
    UserRolesResponseDTO,
    AddPermissionDTO,
    RemovePermissionDTO,
)

__all__ = [
    "CreateRoleDTO",
    "UpdateRoleDTO",
    "RoleResponseDTO",
    "RoleListResponseDTO",
    "AssignRoleDTO",
    "AssignRolesDTO",
    "UserRolesResponseDTO",
    "AddPermissionDTO",
    "RemovePermissionDTO",
]
