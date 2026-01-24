"""
Use cases pour la feature Roles.
"""

from alak_acl.roles.application.usecases.role_usecases import (
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

__all__ = [
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
]
