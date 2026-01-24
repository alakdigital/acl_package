"""
Couche interface de la feature Permissions.
"""

from alak_acl.permissions.interface.dependencies import get_permission_repository, set_permission_dependencies
from alak_acl.permissions.interface.routes import router

__all__ = [
    "router",
    "set_permission_dependencies",
    "get_permission_repository",
]
