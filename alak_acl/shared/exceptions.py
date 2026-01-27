"""
Exceptions personnalisées du package fastapi-acl.

Toutes les exceptions héritent de ACLException pour faciliter
la gestion des erreurs au niveau de l'application.
"""

from typing import Optional


class ACLException(Exception):
    """
    Exception de base pour toutes les erreurs du package ACL.

    Attributes:
        message: Message d'erreur descriptif
        status_code: Code HTTP associé à l'erreur
        error_code: Code d'erreur interne pour le debugging
    """

    def __init__(
        self,
        message: str = "Une erreur ACL s'est produite",
        status_code: int = 500,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "ACL_ERROR"
        super().__init__(self.message)


# ============================================
# Exceptions d'authentification
# ============================================


class AuthenticationError(ACLException):
    """Erreur générique d'authentification."""

    def __init__(self, message: str = "Erreur d'authentification"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
        )


class InvalidCredentialsError(ACLException):
    """Identifiants invalides (username ou password incorrect)."""

    def __init__(self, message: str = "Identifiants invalides"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_CREDENTIALS",
        )


class InvalidTokenError(ACLException):
    """Token JWT invalide ou expiré."""

    def __init__(self, message: str = "Token invalide ou expiré"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_TOKEN",
        )


class TokenExpiredError(ACLException):
    """Token JWT expiré."""

    def __init__(self, message: str = "Token expiré"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="TOKEN_EXPIRED",
        )


# ============================================
# Exceptions utilisateur
# ============================================


class UserNotFoundError(ACLException):
    """Utilisateur non trouvé."""

    def __init__(self, message: str = "Utilisateur non trouvé"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="USER_NOT_FOUND",
        )


class UserNotActiveError(ACLException):
    """Utilisateur désactivé."""

    def __init__(self, message: str = "Compte utilisateur désactivé"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="USER_NOT_ACTIVE",
        )


class UserAlreadyExistsError(ACLException):
    """Utilisateur déjà existant (username ou email)."""

    def __init__(self, message: str = "Un utilisateur avec ces identifiants existe déjà"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="USER_ALREADY_EXISTS",
        )


class UserNotVerifiedError(ACLException):
    """Utilisateur non vérifié."""

    def __init__(self, message: str = "Compte utilisateur non vérifié"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="USER_NOT_VERIFIED",
        )


# ============================================
# Exceptions de permissions
# ============================================


class PermissionDeniedError(ACLException):
    """Permission refusée."""

    def __init__(self, message: str = "Permission refusée"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="PERMISSION_DENIED",
        )


class PermissionNotFoundError(ACLException):
    """Permission non trouvée."""

    def __init__(self, message: str = "Permission non trouvée"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="PERMISSION_NOT_FOUND",
        )


class PermissionAlreadyExistsError(ACLException):
    """Permission déjà existante."""

    def __init__(self, message: str = "Cette permission existe déjà"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="PERMISSION_ALREADY_EXISTS",
        )


# ============================================
# Exceptions de rôles
# ============================================


class RoleNotFoundError(ACLException):
    """Rôle non trouvé."""

    def __init__(self, message: str = "Rôle non trouvé"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="ROLE_NOT_FOUND",
        )


class RoleAlreadyExistsError(ACLException):
    """Rôle déjà existant."""

    def __init__(self, message: str = "Ce rôle existe déjà"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="ROLE_ALREADY_EXISTS",
        )


class RoleInUseError(ACLException):
    """Rôle en cours d'utilisation (assigné à des utilisateurs ou avec des permissions)."""

    def __init__(self, message: str = "Ce rôle est en cours d'utilisation"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="ROLE_IN_USE",
        )


# ============================================
# Exceptions d'infrastructure
# ============================================


class DatabaseConnectionError(ACLException):
    """Erreur de connexion à la base de données."""

    def __init__(self, message: str = "Impossible de se connecter à la base de données"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="DATABASE_CONNECTION_ERROR",
        )


class CacheConnectionError(ACLException):
    """Erreur de connexion au cache."""

    def __init__(self, message: str = "Impossible de se connecter au cache"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="CACHE_CONNECTION_ERROR",
        )


class ConfigurationError(ACLException):
    """Erreur de configuration."""

    def __init__(self, message: str = "Erreur de configuration"):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
        )
