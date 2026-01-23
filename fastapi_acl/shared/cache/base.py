"""
Interface abstraite pour le cache.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheBackend(ABC):
    """
    Interface abstraite pour tous les backends de cache.

    Définit le contrat que chaque implémentation doit respecter.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Établit la connexion au cache.

        Raises:
            CacheConnectionError: Si la connexion échoue
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme la connexion au cache."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache.

        Args:
            key: Clé de la valeur

        Returns:
            Valeur ou None si non trouvée
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Stocke une valeur dans le cache.

        Args:
            key: Clé de la valeur
            value: Valeur à stocker
            ttl: Durée de vie en secondes (optionnel)
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Supprime une valeur du cache.

        Args:
            key: Clé de la valeur

        Returns:
            True si supprimée, False si non trouvée
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe dans le cache.

        Args:
            key: Clé à vérifier

        Returns:
            True si existe, False sinon
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Vide tout le cache."""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Vérifie si le cache est connecté.

        Returns:
            True si connecté, False sinon
        """
        pass

    @property
    @abstractmethod
    def backend_type(self) -> str:
        """
        Retourne le type de backend.

        Returns:
            Type de backend (redis, memory)
        """
        pass
