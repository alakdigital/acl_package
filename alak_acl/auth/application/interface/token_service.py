"""
Interface du service de gestion des tokens JWT.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class ITokenService(ABC):
    """
    Interface abstraite pour le service de tokens JWT.

    Définit le contrat pour la création et validation des tokens.
    """

    @abstractmethod
    def create_access_token(
        self,
        user_id: str,
        username: str,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Crée un token d'accès JWT.

        Args:
            user_id: ID de l'utilisateur (string UUID)
            username: Nom d'utilisateur
            extra_data: Données supplémentaires à inclure dans le token

        Returns:
            Token JWT encodé
        """
        pass

    @abstractmethod
    def create_refresh_token(
        self,
        user_id: str,
        username: str,
    ) -> str:
        """
        Crée un token de rafraîchissement JWT.

        Args:
            user_id: ID de l'utilisateur
            username: Nom d'utilisateur

        Returns:
            Token JWT de rafraîchissement encodé
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Décode et valide un token JWT.

        Args:
            token: Token JWT à décoder

        Returns:
            Payload du token décodé

        Raises:
            InvalidTokenError: Si le token est invalide
            TokenExpiredError: Si le token est expiré
        """
        pass

    @abstractmethod
    def verify_token(self, token: str) -> bool:
        """
        Vérifie si un token est valide sans lever d'exception.

        Args:
            token: Token JWT à vérifier

        Returns:
            True si le token est valide
        """
        pass

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> str:
        """
        Extrait l'ID utilisateur d'un token.

        Args:
            token: Token JWT

        Returns:
            ID de l'utilisateur (string UUID)

        Raises:
            InvalidTokenError: Si le token est invalide
        """
        pass

    @abstractmethod
    def is_refresh_token(self, token: str) -> bool:
        """
        Vérifie si le token est un refresh token.

        Args:
            token: Token JWT

        Returns:
            True si c'est un refresh token
        """
        pass
