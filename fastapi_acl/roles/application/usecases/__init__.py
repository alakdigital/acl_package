"""
Use cases pour la feature Roles.
"""

from .role_usecases import (
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
