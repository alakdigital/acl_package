"""
DTOs pour la réinitialisation de mot de passe.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ForgotPasswordDTO:
    """
    DTO pour la demande de réinitialisation de mot de passe.

    Attributes:
        email: Adresse email de l'utilisateur
    """

    email: str

    def __post_init__(self):
        """Valide les données."""
        self._validate_email()

    def _validate_email(self) -> None:
        """Valide le format de l'email."""
        if not self.email or not self.email.strip():
            raise ValueError("L'email est requis")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.email):
            raise ValueError("Format d'email invalide")


@dataclass(frozen=True)
class ResetPasswordDTO:
    """
    DTO pour la réinitialisation effective du mot de passe.

    Attributes:
        token: Token de réinitialisation (JWT)
        new_password: Nouveau mot de passe
    """

    token: str
    new_password: str

    def __post_init__(self):
        """Valide les données."""
        self._validate_token()
        self._validate_password()

    def _validate_token(self) -> None:
        """Valide que le token est présent."""
        if not self.token or not self.token.strip():
            raise ValueError("Le token de réinitialisation est requis")

    def _validate_password(self) -> None:
        """Valide le nouveau mot de passe."""
        if not self.new_password:
            raise ValueError("Le nouveau mot de passe est requis")

        if len(self.new_password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")

        # Vérifier la complexité
        has_upper = any(c.isupper() for c in self.new_password)
        has_lower = any(c.islower() for c in self.new_password)
        has_digit = any(c.isdigit() for c in self.new_password)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Le mot de passe doit contenir au moins une majuscule, "
                "une minuscule et un chiffre"
            )
