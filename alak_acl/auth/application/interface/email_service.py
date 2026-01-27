"""
Interface du service d'email.

Définit le contrat pour l'envoi d'emails (vérification, reset password, etc.).
"""

from abc import ABC, abstractmethod


class IEmailService(ABC):
    """
    Interface abstraite pour le service d'email.

    Définit le contrat pour l'envoi d'emails. Peut être implémenté
    par SMTPEmailService (production) ou ConsoleEmailService (développement).
    """

    @abstractmethod
    async def send_password_reset_email(
        self,
        to: str,
        username: str,
        reset_link: str,
    ) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe.

        Args:
            to: Adresse email destinataire
            username: Nom d'utilisateur pour personnalisation
            reset_link: Lien complet de réinitialisation

        Returns:
            True si l'email a été envoyé avec succès

        Raises:
            EmailSendError: Si l'envoi échoue
        """
        pass

    @abstractmethod
    async def send_verification_email(
        self,
        to: str,
        username: str,
        verification_link: str,
    ) -> bool:
        """
        Envoie un email de vérification d'adresse.

        Args:
            to: Adresse email destinataire
            username: Nom d'utilisateur pour personnalisation
            verification_link: Lien complet de vérification

        Returns:
            True si l'email a été envoyé avec succès

        Raises:
            EmailSendError: Si l'envoi échoue
        """
        pass

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_text_content: str | None = None,
    ) -> bool:
        """
        Envoie un email générique.

        Args:
            to: Adresse email destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
            plain_text_content: Contenu texte brut (optionnel)

        Returns:
            True si l'email a été envoyé avec succès

        Raises:
            EmailSendError: Si l'envoi échoue
        """
        pass

    @abstractmethod
    async def is_configured(self) -> bool:
        """
        Vérifie si le service d'email est correctement configuré.

        Returns:
            True si le service peut envoyer des emails
        """
        pass
