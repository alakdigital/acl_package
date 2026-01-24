"""
Interface abstraite pour les connexions base de données.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseDatabase(ABC):
    """
    Interface abstraite pour toutes les connexions base de données.

    Définit le contrat que chaque implémentation de DB doit respecter.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Établit la connexion à la base de données.

        Raises:
            DatabaseConnectionError: Si la connexion échoue
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Ferme la connexion à la base de données.
        """
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Vérifie si la connexion est active.

        Returns:
            True si connecté, False sinon
        """
        pass

    @abstractmethod
    def get_session(self) -> Any:
        """
        Retourne une session/connexion pour les opérations.

        Returns:
            Session de base de données
        """
        pass

    @property
    @abstractmethod
    def db_type(self) -> str:
        """
        Retourne le type de base de données.

        Returns:
            Type de DB (mongodb, postgresql, mysql)
        """
        pass
