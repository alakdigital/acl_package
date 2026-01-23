"""
Use Case pour le rafraîchissement de token.
"""

from ..interface.auth_repository import IAuthRepository
from ..interface.token_service import ITokenService
from ...domain.dtos.token_dto import TokenDTO
from ....shared.exceptions import (
    InvalidTokenError,
    UserNotActiveError,
    UserNotFoundError,
)
from ....shared.logging import logger


class RefreshTokenUseCase:
    """
    Use Case pour rafraîchir un token d'accès.

    Gère la logique métier du rafraîchissement :
    - Validation du refresh token
    - Vérification du statut utilisateur
    - Génération d'un nouveau access token

    Attributes:
        auth_repository: Repository pour accéder aux utilisateurs
        token_service: Service pour gérer les tokens
    """

    def __init__(
        self,
        auth_repository: IAuthRepository,
        token_service: ITokenService,
    ):
        """
        Initialise le use case.

        Args:
            auth_repository: Repository d'authentification
            token_service: Service de tokens
        """
        self._auth_repository = auth_repository
        self._token_service = token_service

    async def execute(self, refresh_token: str) -> TokenDTO:
        """
        Rafraîchit un token d'accès.

        Args:
            refresh_token: Token de rafraîchissement

        Returns:
            TokenDTO avec le nouveau access token

        Raises:
            InvalidTokenError: Si le refresh token est invalide
            UserNotActiveError: Si le compte est désactivé
            UserNotFoundError: Si l'utilisateur n'existe plus
        """
        logger.debug("Tentative de rafraîchissement de token")

        # Vérifier que c'est bien un refresh token
        if not self._token_service.is_refresh_token(refresh_token):
            logger.warning("Token fourni n'est pas un refresh token")
            raise InvalidTokenError("Token de rafraîchissement invalide")

        # Décoder le token
        try:
            payload = self._token_service.decode_token(refresh_token)
        except Exception as e:
            logger.warning(f"Erreur décodage refresh token: {e}")
            raise InvalidTokenError("Token de rafraîchissement invalide ou expiré")

        # Récupérer l'utilisateur
        user_id = self._token_service.get_user_id_from_token(refresh_token)
        user = await self._auth_repository.get_by_id(user_id)

        if not user:
            logger.warning(f"Utilisateur non trouvé pour refresh: {user_id}")
            raise UserNotFoundError("Utilisateur non trouvé")

        # Vérifier si le compte est actif
        if not user.is_active:
            logger.warning(f"Compte désactivé pour refresh: {user.username}")
            raise UserNotActiveError("Ce compte a été désactivé")

        # Générer un nouveau access token
        new_access_token = self._token_service.create_access_token(
            user_id=user.id,
            username=user.username,
            extra_data={
                "email": user.email,
                "is_superuser": user.is_superuser,
                "is_verified": user.is_verified,
            },
        )

        logger.info(f"Token rafraîchi pour: {user.username}")

        return TokenDTO(
            access_token=new_access_token,
            refresh_token=refresh_token,  # Garde le même refresh token
            token_type="Bearer",
            expires_in=30 * 60,  # 30 minutes
        )
