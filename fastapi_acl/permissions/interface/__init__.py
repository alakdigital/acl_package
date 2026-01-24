"""
Couche interface de la feature Permissions.
"""

from .routes import router
from .dependencies import (
    set_permission_dependencies,
    get_permission_repository,
)

__all__ = [
    "router",
    "set_permission_dependencies",
    "get_permission_repository",
]
