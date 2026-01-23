"""
Interface du service de hashage de mots de passe.
"""

from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """
    Interface abstraite pour le hashage de mots de passe.

    Définit le contrat pour le hashage et la vérification.
    """

    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Hash un mot de passe.

        Args:
            password: Mot de passe en clair

        Returns:
            Mot de passe hashé
        """
        pass

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie un mot de passe contre son hash.

        Args:
            plain_password: Mot de passe en clair
            hashed_password: Mot de passe hashé

        Returns:
            True si le mot de passe correspond
        """
        pass

    @abstractmethod
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Vérifie si un hash doit être recalculé.

        Utile pour upgrader les hashs après un changement de paramètres.

        Args:
            hashed_password: Mot de passe hashé

        Returns:
            True si le hash doit être recalculé
        """
        pass
