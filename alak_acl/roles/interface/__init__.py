"""
Couche interface de la feature Roles.
"""

from alak_acl.roles.interface.routes import router
from alak_acl.roles.interface.dependencies import (
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
    "router",
    "set_role_dependencies",
    "get_role_repository",
    "get_current_user_roles",
    "get_current_user_permissions",
    "RequireRole",
    "RequireRoles",
    "RequirePermission",
    "RequirePermissions",
]
