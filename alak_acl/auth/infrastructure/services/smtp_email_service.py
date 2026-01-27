"""
Service d'email SMTP pour la production.

Utilise aiosmtplib pour l'envoi asynchrone d'emails.
"""

from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from alak_acl.auth.application.interface.email_service import IEmailService
from alak_acl.shared.exceptions import EmailSendError
from alak_acl.shared.logging import logger


class SMTPEmailService(IEmailService):
    """
    Implémentation du service d'email avec SMTP.

    Nécessite l'installation de aiosmtplib:
        pip install aiosmtplib

    Attributes:
        smtp_server: Serveur SMTP (ex: smtp.gmail.com)
        smtp_port: Port SMTP (587 pour TLS, 465 pour SSL)
        smtp_username: Identifiant SMTP
        smtp_password: Mot de passe SMTP
        from_email: Adresse email source
        use_tls: Utiliser STARTTLS
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: str = "noreply@example.com",
        from_name: str = "alak-acl",
        use_tls: bool = True,
    ):
        """
        Initialise le service SMTP.

        Args:
            smtp_server: Serveur SMTP
            smtp_port: Port SMTP
            smtp_username: Identifiant SMTP
            smtp_password: Mot de passe SMTP
            from_email: Adresse email source
            from_name: Nom affiché de l'expéditeur
            use_tls: Utiliser STARTTLS
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
        self.use_tls = use_tls

    async def send_password_reset_email(
        self,
        to: str,
        username: str,
        reset_link: str,
    ) -> bool:
        """Envoie un email de réinitialisation de mot de passe."""
        subject = f"Réinitialisation de votre mot de passe - {self.from_name}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4A90D9; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background-color: #f9f9f9; }}
        .button {{ display: inline-block; padding: 12px 30px; background-color: #4A90D9;
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Réinitialisation de mot de passe</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{username}</strong>,</p>
            <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
            <p>Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe:</p>
            <p style="text-align: center;">
                <a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>
            </p>
            <p><small>Ce lien expire dans 1 heure.</small></p>
            <p>Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.</p>
        </div>
        <div class="footer">
            <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
        </div>
    </div>
</body>
</html>
"""

        plain_text = f"""
Bonjour {username},

Vous avez demandé la réinitialisation de votre mot de passe.

Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe:
{reset_link}

Ce lien expire dans 1 heure.

Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.
"""

        return await self.send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text,
        )

    async def send_verification_email(
        self,
        to: str,
        username: str,
        verification_link: str,
    ) -> bool:
        """Envoie un email de vérification d'adresse."""
        subject = f"Vérifiez votre adresse email - {self.from_name}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background-color: #f9f9f9; }}
        .button {{ display: inline-block; padding: 12px 30px; background-color: #28a745;
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bienvenue!</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{username}</strong>,</p>
            <p>Merci de vous être inscrit! Veuillez vérifier votre adresse email.</p>
            <p style="text-align: center;">
                <a href="{verification_link}" class="button">Vérifier mon email</a>
            </p>
        </div>
        <div class="footer">
            <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
        </div>
    </div>
</body>
</html>
"""

        plain_text = f"""
Bonjour {username},

Merci de vous être inscrit! Veuillez vérifier votre adresse email en cliquant sur le lien:
{verification_link}
"""

        return await self.send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text,
        )

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_text_content: Optional[str] = None,
    ) -> bool:
        """Envoie un email via SMTP."""
        if not await self.is_configured():
            logger.error("Service SMTP non configuré")
            raise EmailSendError("Le service SMTP n'est pas configuré")

        try:
            # Import aiosmtplib uniquement si nécessaire
            try:
                import aiosmtplib
            except ImportError:
                raise EmailSendError(
                    "aiosmtplib n'est pas installé. "
                    "Installez-le avec: pip install aiosmtplib"
                )

            # Créer le message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to

            # Ajouter le contenu texte si fourni
            if plain_text_content:
                msg.attach(MIMEText(plain_text_content, "plain", "utf-8"))

            # Ajouter le contenu HTML
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            # Envoyer via SMTP
            if self.use_tls:
                # STARTTLS sur port 587
                await aiosmtplib.send(
                    msg,
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    start_tls=True,
                )
            else:
                # SSL direct sur port 465
                await aiosmtplib.send(
                    msg,
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    use_tls=True,
                )

            logger.info(f"Email envoyé à {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Erreur d'envoi email à {to}: {e}")
            raise EmailSendError(f"Impossible d'envoyer l'email: {e}")

    async def is_configured(self) -> bool:
        """Vérifie si le service SMTP est configuré."""
        return bool(
            self.smtp_server
            and self.smtp_port
            and self.from_email
        )
