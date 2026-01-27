"""
Service de gestion des tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError, ExpiredSignatureError


from alak_acl.auth.application.interface.token_service import ITokenService
from alak_acl.shared.config import ACLConfig
from alak_acl.shared.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    ResetTokenExpiredError,
    ResetTokenInvalidError,
)
from alak_acl.shared.logging import logger


class JWTTokenService(ITokenService):
    """
    Implémentation du service de tokens JWT avec python-jose.

    Attributes:
        config: Configuration ACL
    """

    TOKEN_TYPE_ACCESS = "access"
    TOKEN_TYPE_REFRESH = "refresh"
    TOKEN_TYPE_RESET = "reset"

    def __init__(self, config: ACLConfig):
        """
        Initialise le service.

        Args:
            config: Configuration ACL
        """
        self._config = config
        self._secret_key = config.jwt_secret_key
        self._algorithm = config.jwt_algorithm
        self._access_expire_minutes = config.jwt_access_token_expire_minutes
        self._refresh_expire_days = config.jwt_refresh_token_expire_days
        self._reset_expire_minutes = getattr(config, 'reset_token_expire_minutes', 60)

    def create_access_token(
        self,
        user_id: str,
        username: str,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Crée un token d'accès JWT."""
        expire = datetime.utcnow() + timedelta(minutes=self._access_expire_minutes)

        payload = {
            "sub": user_id,
            "username": username,
            "type": self.TOKEN_TYPE_ACCESS,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        if extra_data:
            payload.update(extra_data)

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        logger.debug(f"Access token créé pour: {username}")
        return token

    def create_refresh_token(
        self,
        user_id: str,
        username: str,
    ) -> str:
        """Crée un token de rafraîchissement JWT."""
        expire = datetime.utcnow() + timedelta(days=self._refresh_expire_days)

        payload = {
            "sub": user_id,
            "username": username,
            "type": self.TOKEN_TYPE_REFRESH,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        logger.debug(f"Refresh token créé pour: {username}")
        return token

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Décode et valide un token JWT."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            return payload

        except ExpiredSignatureError:
            logger.warning("Token expiré")
            raise TokenExpiredError("token", "Le token a expiré")

        except JWTError as e:
            logger.warning(f"Erreur de décodage JWT: {e}")
            raise InvalidTokenError("Token", "Token invalide")

    def verify_token(self, token: str) -> bool:
        """Vérifie si un token est valide."""
        try:
            self.decode_token(token)
            return True
        except (InvalidTokenError, TokenExpiredError):
            return False

    def get_user_id_from_token(self, token: str) -> str:
        """Extrait l'ID utilisateur d'un token."""
        payload = self.decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenError("Token", "Token invalide: ID utilisateur manquant")

        return user_id

    def is_refresh_token(self, token: str) -> bool:
        """Vérifie si le token est un refresh token."""
        try:
            payload = self.decode_token(token)
            return payload.get("type") == self.TOKEN_TYPE_REFRESH
        except (InvalidTokenError, TokenExpiredError):
            return False

    def get_token_expiry(self) -> int:
        """
        Retourne la durée de validité du access token en secondes.

        Returns:
            Durée en secondes
        """
        return self._access_expire_minutes * 60

    def create_reset_token(
        self,
        user_id: str,
        email: str,
    ) -> str:
        """Crée un token de réinitialisation de mot de passe."""
        expire = datetime.utcnow() + timedelta(minutes=self._reset_expire_minutes)

        payload = {
            "sub": user_id,
            "email": email,
            "type": self.TOKEN_TYPE_RESET,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        logger.debug(f"Reset token créé pour: {email}")
        return token

    def decode_reset_token(self, token: str) -> Dict[str, Any]:
        """Décode et valide un token de réinitialisation."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )

            # Vérifier que c'est bien un reset token
            if payload.get("type") != self.TOKEN_TYPE_RESET:
                raise ResetTokenInvalidError("Ce n'est pas un token de réinitialisation")

            return payload

        except ExpiredSignatureError:
            logger.warning("Reset token expiré")
            raise ResetTokenExpiredError()

        except JWTError as e:
            logger.warning(f"Erreur de décodage reset token: {e}")
            raise ResetTokenInvalidError()

    def is_reset_token(self, token: str) -> bool:
        """Vérifie si le token est un token de réinitialisation."""
        try:
            payload = self.decode_token(token)
            return payload.get("type") == self.TOKEN_TYPE_RESET
        except (InvalidTokenError, TokenExpiredError):
            return False
