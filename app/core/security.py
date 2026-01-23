"""Utilitaires de sécurité : JWT, hashing, tokens."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


# Configuration du hashing des passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash un mot de passe."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any]) -> str:
    """
    Crée un access token JWT.

    Args:
        data: Données à encoder dans le token (généralement user_id, email, role)
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Crée un refresh token JWT.

    Args:
        data: Données à encoder dans le token (généralement user_id)
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Décode et valide un token JWT.

    Args:
        token: Token JWT à décoder

    Returns:
        Payload du token si valide, None sinon
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    """
    Vérifie que le token est du type attendu.

    Args:
        payload: Payload du token
        expected_type: Type attendu ("access" ou "refresh")
    """
    return payload.get("type") == expected_type
