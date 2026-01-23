"""
DTOs (Data Transfer Objects) de la feature Auth.
"""

from .login_dto import LoginDTO
from .register_dto import RegisterDTO
from .token_dto import TokenDTO

__all__ = [
    "LoginDTO",
    "RegisterDTO",
    "TokenDTO",
]
