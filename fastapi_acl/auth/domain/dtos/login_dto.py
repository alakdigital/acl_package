"""
DTO pour la connexion utilisateur.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginDTO:
    """
    Data Transfer Object pour la connexion.

    Immutable (frozen) pour garantir l'intégrité des données.

    Attributes:
        username: Nom d'utilisateur ou email
        password: Mot de passe en clair
    """

    username: str
    password: str

    def __post_init__(self):
        """Valide les données après initialisation."""
        if not self.username or not self.username.strip():
            raise ValueError("Le nom d'utilisateur est requis")
        if not self.password:
            raise ValueError("Le mot de passe est requis")
