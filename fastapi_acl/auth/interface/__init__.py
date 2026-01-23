"""
Couche Interface - Routes API et dépendances FastAPI.
"""

from .schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    MessageResponse,
)
from .dependencies import get_current_user, get_current_active_user
from .api import router as auth_router
from .admin.routes import router as admin_router

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
