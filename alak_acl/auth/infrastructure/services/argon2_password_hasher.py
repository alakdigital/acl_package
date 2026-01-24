"""
Service de hashage de mots de passe avec Argon2.

Argon2 est l'algorithme recommandé par OWASP pour le hashage de mots de passe.
Il est le gagnant du Password Hashing Competition (2015).
"""

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from alak_acl.auth.application.interface.password_hasher import IPasswordHasher


class Argon2PasswordHasher(IPasswordHasher):
    """
    Implémentation du hashage de mots de passe avec Argon2.

    Argon2 est résistant aux attaques GPU et ASIC, et ne souffre pas
    de la limitation de 72 bytes de bcrypt.

    Attributes:
        _hasher: Instance du hasher Argon2
    """

    def __init__(
        self,
        time_cost: int = 3,
        memory_cost: int = 65536,
        parallelism: int = 4,
    ):
        """
        Initialise le hasher Argon2.

        Args:
            time_cost: Nombre d'itérations (défaut: 3)
            memory_cost: Mémoire en KB (défaut: 64MB)
            parallelism: Nombre de threads parallèles (défaut: 4)
        """
        self._hasher = Argon2Hasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
        )

    def hash(self, password: str) -> str:
        """
        Hash un mot de passe avec Argon2.

        Args:
            password: Mot de passe en clair

        Returns:
            Hash Argon2 du mot de passe
        """
        return self._hasher.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie un mot de passe contre son hash.

        Args:
            plain_password: Mot de passe en clair
            hashed_password: Hash stocké

        Returns:
            True si le mot de passe correspond, False sinon
        """
        try:
            self._hasher.verify(hashed_password, plain_password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False
        except Exception:
            return False

    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Vérifie si un hash doit être recalculé.

        Retourne True si les paramètres de hashage ont changé.

        Args:
            hashed_password: Hash à vérifier

        Returns:
            True si le hash doit être recalculé
        """
        try:
            return self._hasher.check_needs_rehash(hashed_password)
        except Exception:
            return True
