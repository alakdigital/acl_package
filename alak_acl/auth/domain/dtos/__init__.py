"""
DTOs (Data Transfer Objects) de la feature Auth.
"""

from alak_acl.auth.domain.dtos.login_dto import LoginDTO
from alak_acl.auth.domain.dtos.register_dto import RegisterDTO
from alak_acl.auth.domain.dtos.token_dto import TokenDTO


__all__ = [
    "LoginDTO",
    "RegisterDTO",
    "TokenDTO",
]
