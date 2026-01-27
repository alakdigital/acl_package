"""
Use case pour la réinitialisation effective du mot de passe.
"""

from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.application.interface.token_service import ITokenService
from alak_acl.auth.application.interface.password_hasher import IPasswordHasher
from alak_acl.auth.domain.dtos.password_reset_dto import ResetPasswordDTO
from alak_acl.shared.exceptions import (
    ResetTokenInvalidError,
    UserNotFoundError,
    UserNotActiveError,
)
from alak_acl.shared.logging import logger


class ResetPasswordUseCase:
    """
    Use case pour réinitialiser le mot de passe avec un token.

    Valide le token de reset, vérifie l'utilisateur, et met à jour
    le mot de passe avec un nouveau hash.
    """

    def __init__(
        self,
        auth_repository: IAuthRepository,
        token_service: ITokenService,
        password_hasher: IPasswordHasher,
    ):
        """
        Initialise le use case.

        Args:
            auth_repository: Repository d'authentification
            token_service: Service de tokens JWT
            password_hasher: Service de hashage des mots de passe
        """
        self._auth_repository = auth_repository
        self._token_service = token_service
        self._password_hasher = password_hasher

    async def execute(self, dto: ResetPasswordDTO) -> bool:
        """
        Réinitialise le mot de passe.

        Args:
            dto: DTO contenant le token et le nouveau mot de passe

        Returns:
            True si le mot de passe a été réinitialisé

        Raises:
            ResetTokenInvalidError: Si le token est invalide
            ResetTokenExpiredError: Si le token est expiré
            UserNotFoundError: Si l'utilisateur n'existe plus
            UserNotActiveError: Si le compte est désactivé
        """
        logger.info("Tentative de réinitialisation de mot de passe")

        # Décoder et valider le token (peut lever ResetTokenInvalidError ou ResetTokenExpiredError)
        payload = self._token_service.decode_reset_token(dto.token)

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise ResetTokenInvalidError("Token de réinitialisation malformé")

        # Récupérer l'utilisateur
        user = await self._auth_repository.get_by_id(user_id)

        if not user:
            logger.warning(f"Utilisateur non trouvé pour reset: {user_id}")
            raise UserNotFoundError("user_id", "L'utilisateur n'existe plus")

        # Vérifier que l'email correspond (sécurité supplémentaire)
        if user.email != email:
            logger.warning(f"Email mismatch pour reset: {email} vs {user.email}")
            raise ResetTokenInvalidError("Token de réinitialisation invalide")

        # Vérifier que le compte est actif
        if not user.is_active:
            logger.warning(f"Compte désactivé pour reset: {user_id}")
            raise UserNotActiveError("Le compte est désactivé")

        # Hasher le nouveau mot de passe
        hashed_password = self._password_hasher.hash(dto.new_password)

        # Mettre à jour le mot de passe
        user.hashed_password = hashed_password
        user.mark_updated()

        await self._auth_repository.update_user(user)

        logger.info(f"Mot de passe réinitialisé pour: {user.username}")
        return True
