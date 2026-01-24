"""
DTO pour les tokens JWT.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TokenDTO:
    """
    Data Transfer Object pour les tokens d'authentification.

    Immutable (frozen) pour garantir l'intégrité des données.

    Attributes:
        access_token: Token d'accès JWT
        refresh_token: Token de rafraîchissement JWT
        token_type: Type de token (Bearer)
        expires_in: Durée de validité en secondes
    """

    access_token: str
    token_type: str = "Bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None

    def to_dict(self) -> dict:
        """
        Convertit le DTO en dictionnaire.

        Returns:
            Dictionnaire représentant les tokens
        """
        result = {
            "access_token": self.access_token,
            "token_type": self.token_type,
        }
        if self.refresh_token:
            result["refresh_token"] = self.refresh_token
        if self.expires_in:
            result["expires_in"] = self.expires_in
        return result
