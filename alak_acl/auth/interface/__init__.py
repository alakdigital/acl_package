"""
Couche Interface - Routes API et dépendances FastAPI.
"""

from alak_acl.auth.interface.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    MessageResponse,
)
from alak_acl.auth.interface.dependencies import get_current_user, get_current_active_user
from alak_acl.auth.interface.api import router as auth_router
from alak_acl.auth.interface.admin.routes import router as admin_router

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "UserResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "MessageResponse",
    "get_current_user",
    "get_current_active_user",
    "auth_router",
    "admin_router",
]
