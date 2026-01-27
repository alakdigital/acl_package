"""
Module shared - Code partagé entre toutes les features.

Ce module contient les configurations, connexions DB, cache et exceptions
utilisées par l'ensemble du package fastapi-acl.
"""

from alak_acl.shared.config import ACLConfig
from alak_acl.shared.exceptions import (
    ACLException,
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotActiveError,
    UserAlreadyExistsError,
    PermissionDeniedError,
    PermissionInUseError,
    RoleNotFoundError,
    RoleInUseError,
    DatabaseConnectionError,
    CacheConnectionError,
)

__all__ = [
    "ACLConfig",
    "ACLException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "UserNotActiveError",
    "UserAlreadyExistsError",
    "PermissionDeniedError",
    "PermissionInUseError",
    "RoleNotFoundError",
    "RoleInUseError",
    "DatabaseConnectionError",
    "CacheConnectionError",
]
