from abc import ABC, abstractmethod
from typing import TypeVar, Generic


T = TypeVar("T")


class IUseCase(ABC, Generic[T]):
    """Interface générique pour les cas d'usage.

    Définit le contrat de base pour tous les cas d'usage de l'application.
    Chaque use case doit implémenter la méthode execute() avec ses propres
    paramètres et type de retour.
    """

    @abstractmethod
    async def execute(self, *args, **kwargs) -> T:
        """
        Exécute le cas d'usage.

        Returns:
            Résultat de l'exécution
        """
        pass
