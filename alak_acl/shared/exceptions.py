from typing import List, Dict

class ACLException(Exception):
    """
    Exception de base pour toutes les erreurs ACL.
    Format uniforme pour JSONResponse.
    """

    def __init__(
        self,
        message: str = "Une erreur ACL s'est produite",
        status_code: int = 500,
        details: List[Dict[str, str]] = None,
        error_code: str = "ACL_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or []
        self.error_code = error_code
        super().__init__(self.message)


# ============================================
# Exceptions d'authentification
# ============================================

class AuthenticationError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Erreur d'authentification",
            status_code=401,
            details=[{"field": field, "message": message}],
            error_code="AUTHENTICATION_ERROR",
        )


class InvalidCredentialsError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Identifiants invalides",
            status_code=401,
            details=[{"field": field, "message": message}],
            error_code="INVALID_CREDENTIALS",
        )


class InvalidTokenError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Token invalide ou expiré",
            status_code=401,
            details=[{"field": field, "message": message}],
            error_code="INVALID_TOKEN",
        )


class TokenExpiredError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Token expiré",
            status_code=401,
            details=[{"field": field, "message": message}],
            error_code="TOKEN_EXPIRED",
        )


class ResetTokenExpiredError(ACLException):
    """Token de réinitialisation de mot de passe expiré."""

    def __init__(self, message: str = "Le lien de réinitialisation a expiré"):
        super().__init__(
            message=message,
            status_code=401,
            details=[{"field": "token", "message": message}],
            error_code="RESET_TOKEN_EXPIRED",
        )


class ResetTokenInvalidError(ACLException):
    """Token de réinitialisation de mot de passe invalide."""

    def __init__(self, message: str = "Le lien de réinitialisation est invalide"):
        super().__init__(
            message=message,
            status_code=401,
            details=[{"field": "token", "message": message}],
            error_code="RESET_TOKEN_INVALID",
        )


class EmailSendError(ACLException):
    """Erreur lors de l'envoi d'un email."""

    def __init__(self, message: str = "Impossible d'envoyer l'email"):
        super().__init__(
            message=message,
            status_code=503,
            details=[{"field": "email", "message": message}],
            error_code="EMAIL_SEND_ERROR",
        )


# ============================================
# Exceptions utilisateur
# ============================================

class UserNotFoundError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Utilisateur non trouvé",
            status_code=404,
            details=[{"field": field, "message": message}],
            error_code="USER_NOT_FOUND",
        )


class UserNotActiveError(ACLException):
    def __init__(self, message: str):
        super().__init__(
            message="Compte utilisateur désactivé",
            status_code=403,
            details=[{"field": 'is_active', "message": message}],
            error_code="USER_NOT_ACTIVE",
        )


class UserAlreadyExistsError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Utilisateur déjà existant",
            status_code=409,
            details=[{"field": field, "message": message}],
            error_code="USER_ALREADY_EXISTS",
        )


class UserNotVerifiedError(ACLException):
    def __init__(self, message: str):
        super().__init__(
            message="Compte utilisateur non vérifié",
            status_code=403,
            details=[{"field": "email", "message": message}],
            error_code="USER_NOT_VERIFIED",
        )


# ============================================
# Exceptions permissions
# ============================================
class PermissionInUseError(ACLException):
    """
    Permission en cours d'utilisation
    (assignée à des rôles ou utilisateurs).
    """

    def __init__(self, message: str):
        super().__init__(
            message="Permission en cours d'utilisation",
            status_code=409,
            details=message,
            error_code="PERMISSION_IN_USE",
        )

class PermissionDeniedError(ACLException):
    def __init__(self, message: str):
        super().__init__(
            message="Permission refusée",
            status_code=403,
            details=message,
            error_code="PERMISSION_DENIED",
        )


class PermissionNotFoundError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Permission non trouvée",
            status_code=404,
            details=[{"field": field, "message": message}],
            error_code="PERMISSION_NOT_FOUND",
        )


class PermissionAlreadyExistsError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Permission déjà existante",
            status_code=409,
            details=[{"field": field, "message": message}],
            error_code="PERMISSION_ALREADY_EXISTS",
        )


# ============================================
# Exceptions rôles
# ============================================

class RoleNotFoundError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Rôle non trouvé",
            status_code=404,
            details=[{"field": field, "message": message}],
            error_code="ROLE_NOT_FOUND",
        )


class RoleAlreadyExistsError(ACLException):
    def __init__(self, field: str, message: str):
        super().__init__(
            message="Rôle déjà existant",
            status_code=409,
            details=[{"field": field, "message": message}],
            error_code="ROLE_ALREADY_EXISTS",
        )


class RoleInUseError(ACLException):
    def __init__(self, message: str):
        super().__init__(
            message="Rôle en cours d'utilisation",
            status_code=409,
            details=message,
            error_code="ROLE_IN_USE",
        )


# ============================================
# Exceptions infrastructure
# ============================================

class DatabaseConnectionError(ACLException):
    def __init__(self, message: str):
        super().__init__(
            message="Erreur de connexion à la base de données",
            status_code=503,
            details=message,
            error_code="DATABASE_CONNECTION_ERROR",
        )


class CacheConnectionError(ACLException):
    def __init__(self, message: str):
        super().__init__(
            message="Erreur de connexion au cache",
            status_code=503,
            details=message,
            error_code="CACHE_CONNECTION_ERROR",
        )


class ConfigurationError(ACLException):
    def __init__(self, message: str):
        super().__init__(
            message="Erreur de configuration",
            status_code=500,
            details=message,
            error_code="CONFIGURATION_ERROR",
        )
