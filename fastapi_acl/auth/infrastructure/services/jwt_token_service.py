"""
Service de gestion des tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from jose import jwt, JWTError, ExpiredSignatureError

from ...application.interface.token_service import ITokenService
from ....shared.config import ACLConfig
from ....shared.exceptions import InvalidTokenError, TokenExpiredError
from ....shared.logging import logger


class JWTTokenService(ITokenService):
    """
    Implémentation du service de tokens JWT avec python-jose.

    Attributes:
        config: Configuration ACL
    """

    TOKEN_TYPE_ACCESS = "access"
    TOKEN_TYPE_REFRESH = "refresh"

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

    def create_access_token(
        self,
        user_id: UUID,
        username: str,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Crée un token d'accès JWT."""
        expire = datetime.utcnow() + timedelta(minutes=self._access_expire_minutes)

        payload = {
            "sub": str(user_id),
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
        user_id: UUID,
        username: str,
    ) -> str:
        """Crée un token de rafraîchissement JWT."""
        expire = datetime.utcnow() + timedelta(days=self._refresh_expire_days)

        payload = {
            "sub": str(user_id),
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
            raise TokenExpiredError("Le token a expiré")

        except JWTError as e:
            logger.warning(f"Erreur de décodage JWT: {e}")
            raise InvalidTokenError("Token invalide")

    def verify_token(self, token: str) -> bool:
        """Vérifie si un token est valide."""
        try:
            self.decode_token(token)
            return True
        except (InvalidTokenError, TokenExpiredError):
            return False

    def get_user_id_from_token(self, token: str) -> UUID:
        """Extrait l'ID utilisateur d'un token."""
        payload = self.decode_token(token)
        user_id_str = payload.get("sub")

        if not user_id_str:
            raise InvalidTokenError("Token invalide: ID utilisateur manquant")

        try:
            return UUID(user_id_str)
        except ValueError:
            raise InvalidTokenError("Token invalide: format ID incorrect")

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
