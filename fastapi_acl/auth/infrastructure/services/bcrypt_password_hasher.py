"""
Service de hashage de mots de passe avec bcrypt.
"""

from passlib.context import CryptContext

from ...application.interface.password_hasher import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """
    Implémentation du hashage de mots de passe avec bcrypt.

    Utilise passlib pour la gestion des hashs.
    Configuration: bcrypt avec deprecated="auto" pour supporter
    les anciens hashs.
    """

    def __init__(self, rounds: int = 12):
        """
        Initialise le hasher.

        Args:
            rounds: Nombre de rounds bcrypt (défaut: 12)
        """
        self._context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=rounds,
        )

    def hash(self, password: str) -> str:
        """Hash un mot de passe."""
        return self._context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe contre son hash."""
        try:
            return self._context.verify(plain_password, hashed_password)
        except Exception:
            return False

    def needs_rehash(self, hashed_password: str) -> bool:
        """Vérifie si un hash doit être recalculé."""
        return self._context.needs_update(hashed_password)
