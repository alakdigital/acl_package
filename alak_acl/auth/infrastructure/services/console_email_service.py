"""
Service d'email pour le développement (affiche dans la console).

Ce service est utilisé par défaut quand SMTP n'est pas configuré.
Il affiche les emails dans les logs pour faciliter le développement.
"""

from alak_acl.auth.application.interface.email_service import IEmailService
from alak_acl.shared.logging import logger


class ConsoleEmailService(IEmailService):
    """
    Implémentation du service d'email qui affiche dans la console.

    Utilisé pour le développement local sans serveur SMTP.
    Les liens de réinitialisation sont affichés dans les logs.
    """

    def __init__(self, app_name: str = "alak-acl"):
        """
        Initialise le service.

        Args:
            app_name: Nom de l'application pour les logs
        """
        self._app_name = app_name

    async def send_password_reset_email(
        self,
        to: str,
        username: str,
        reset_link: str,
    ) -> bool:
        """Affiche l'email de réinitialisation dans la console."""
        logger.info("=" * 60)
        logger.info("📧 EMAIL DE RÉINITIALISATION DE MOT DE PASSE")
        logger.info("=" * 60)
        logger.info(f"À: {to}")
        logger.info(f"Utilisateur: {username}")
        logger.info(f"Sujet: Réinitialisation de votre mot de passe - {self._app_name}")
        logger.info("-" * 60)
        logger.info("Contenu:")
        logger.info(f"  Bonjour {username},")
        logger.info("")
        logger.info("  Vous avez demandé la réinitialisation de votre mot de passe.")
        logger.info("  Cliquez sur le lien ci-dessous (valide 1 heure):")
        logger.info("")
        logger.info(f"  🔗 {reset_link}")
        logger.info("")
        logger.info("  Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.")
        logger.info("-" * 60)
        logger.info("=" * 60)
        return True

    async def send_verification_email(
        self,
        to: str,
        username: str,
        verification_link: str,
    ) -> bool:
        """Affiche l'email de vérification dans la console."""
        logger.info("=" * 60)
        logger.info("📧 EMAIL DE VÉRIFICATION D'ADRESSE")
        logger.info("=" * 60)
        logger.info(f"À: {to}")
        logger.info(f"Utilisateur: {username}")
        logger.info(f"Sujet: Vérifiez votre adresse email - {self._app_name}")
        logger.info("-" * 60)
        logger.info("Contenu:")
        logger.info(f"  Bienvenue {username}!")
        logger.info("")
        logger.info("  Cliquez sur le lien ci-dessous pour vérifier votre email:")
        logger.info("")
        logger.info(f"  🔗 {verification_link}")
        logger.info("-" * 60)
        logger.info("=" * 60)
        return True

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_text_content: str | None = None,
    ) -> bool:
        """Affiche un email générique dans la console."""
        logger.info("=" * 60)
        logger.info("📧 EMAIL GÉNÉRIQUE")
        logger.info("=" * 60)
        logger.info(f"À: {to}")
        logger.info(f"Sujet: {subject}")
        logger.info("-" * 60)
        if plain_text_content:
            logger.info("Contenu (texte):")
            for line in plain_text_content.split("\n"):
                logger.info(f"  {line}")
        else:
            logger.info("Contenu (HTML):")
            # Afficher un résumé du HTML
            logger.info(f"  {html_content[:200]}...")
        logger.info("-" * 60)
        logger.info("=" * 60)
        return True

    async def is_configured(self) -> bool:
        """Le service console est toujours configuré."""
        return True
