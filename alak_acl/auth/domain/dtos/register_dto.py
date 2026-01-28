"""
DTO pour l'inscription utilisateur.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterDTO:
    """
    Data Transfer Object pour l'inscription.

    Immutable (frozen) pour garantir l'intégrité des données.

    Note SaaS:
        Le tenant_id n'est PAS inclus ici car un utilisateur
        peut appartenir à plusieurs tenants. L'association
        user <-> tenant se fait via la table de membership
        après création du compte.

    Attributes:
        username: Nom d'utilisateur unique (globalement)
        email: Adresse email unique (globalement)
        password: Mot de passe en clair
    """

    username: str
    email: str
    password: str

    def __post_init__(self):
        """Valide les données après initialisation."""
        self._validate_username()
        self._validate_email()
        self._validate_password()

    def _validate_username(self) -> None:
        """Valide le nom d'utilisateur."""
        if not self.username or not self.username.strip():
            raise ValueError("Le nom d'utilisateur est requis")

        if len(self.username) < 3:
            raise ValueError("Le nom d'utilisateur doit faire au moins 3 caractères")

        if len(self.username) > 50:
            raise ValueError("Le nom d'utilisateur ne peut pas dépasser 50 caractères")

        if not re.match(r"^[a-zA-Z0-9_-]+$", self.username):
            raise ValueError(
                "Le nom d'utilisateur ne peut contenir que des lettres, "
                "chiffres, tirets et underscores"
            )

    def _validate_email(self) -> None:
        """Valide l'adresse email."""
        if not self.email or not self.email.strip():
            raise ValueError("L'email est requis")

        # Regex simple pour validation email
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.email):
            raise ValueError("Format d'email invalide")

    def _validate_password(self) -> None:
        """Valide le mot de passe."""
        if not self.password:
            raise ValueError("Le mot de passe est requis")

        if len(self.password) < 8:
            raise ValueError("Le mot de passe doit faire au moins 8 caractères")

        if len(self.password) > 128:
            raise ValueError("Le mot de passe ne peut pas dépasser 128 caractères")
