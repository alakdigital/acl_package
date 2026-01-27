"""
Use case pour la demande de réinitialisation de mot de passe.
"""

from typing import Optional

from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.application.interface.token_service import ITokenService
from alak_acl.auth.application.interface.email_service import IEmailService
from alak_acl.auth.domain.dtos.password_reset_dto import ForgotPasswordDTO
from alak_acl.shared.logging import logger


class ForgotPasswordUseCase:
    """
    Use case pour demander la réinitialisation d'un mot de passe.

    Génère un token de reset et envoie un email avec le lien.
    Pour des raisons de sécurité, retourne toujours un succès même si
    l'email n'existe pas (évite l'énumération des utilisateurs).
    """

    def __init__(
        self,
        auth_repository: IAuthRepository,
        token_service: ITokenService,
        email_service: IEmailService,
        reset_url_base: Optional[str] = None,
    ):
        """
        Initialise le use case.

        Args:
            auth_repository: Repository d'authentification
            token_service: Service de tokens JWT
            email_service: Service d'envoi d'emails
            reset_url_base: URL de base pour le lien de reset
                           (ex: https://app.example.com/reset-password)
        """
        self._auth_repository = auth_repository
        self._token_service = token_service
        self._email_service = email_service
        self._reset_url_base = reset_url_base or "http://localhost:3000/reset-password"

    async def execute(self, dto: ForgotPasswordDTO) -> bool:
        """
        Traite la demande de réinitialisation.

        Args:
            dto: DTO contenant l'email

        Returns:
            True (toujours, pour ne pas révéler si l'email existe)
        """
        logger.info(f"Demande de réinitialisation pour: {dto.email}")

        # Chercher l'utilisateur par email
        user = await self._auth_repository.get_by_email(dto.email)

        if not user:
            # Ne pas révéler que l'email n'existe pas
            logger.debug(f"Email non trouvé: {dto.email} (réponse identique)")
            return True

        if not user.is_active:
            # Compte désactivé - ne pas révéler non plus
            logger.debug(f"Compte désactivé pour: {dto.email}")
            return True

        # Générer le token de reset
        reset_token = self._token_service.create_reset_token(
            user_id=user.id,
            email=user.email,
        )

        # Construire le lien de réinitialisation
        reset_link = f"{self._reset_url_base}?token={reset_token}"

        # Envoyer l'email
        try:
            await self._email_service.send_password_reset_email(
                to=user.email,
                username=user.username,
                reset_link=reset_link,
            )
            logger.info(f"Email de réinitialisation envoyé à: {user.email}")
        except Exception as e:
            # Log l'erreur mais ne pas la propager à l'utilisateur
            logger.error(f"Erreur d'envoi email: {e}")
            # On retourne quand même True pour ne pas révéler d'info

        return True
