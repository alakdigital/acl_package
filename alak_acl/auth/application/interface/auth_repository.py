"""
Interface du repository d'authentification.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from alak_acl.auth.domain.entities.auth_user import AuthUser



class IAuthRepository(ABC):
    """
    Interface abstraite pour le repository d'authentification.

    Définit le contrat que chaque implémentation de repository
    (MongoDB, PostgreSQL, MySQL) doit respecter.
    """

    @abstractmethod
    async def create_user(self, user: AuthUser) -> AuthUser:
        """
        Crée un nouvel utilisateur.

        Args:
            user: Entité utilisateur à créer

        Returns:
            Utilisateur créé avec son ID

        Raises:
            UserAlreadyExistsError: Si username ou email existe déjà
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[AuthUser]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: ID de l'utilisateur (string)

        Returns:
            Utilisateur ou None si non trouvé
        """
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[AuthUser]:
        """
        Récupère un utilisateur par son nom d'utilisateur.

        Args:
            username: Nom d'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[AuthUser]:
        """
        Récupère un utilisateur par son email.

        Args:
            email: Adresse email

        Returns:
            Utilisateur ou None si non trouvé
        """
        pass

    @abstractmethod
    async def update_user(self, user: AuthUser) -> AuthUser:
        """
        Met à jour un utilisateur existant.

        Args:
            user: Entité utilisateur avec les modifications

        Returns:
            Utilisateur mis à jour

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas
        """
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """
        Supprime un utilisateur.

        Args:
            user_id: ID de l'utilisateur (string)

        Returns:
            True si supprimé, False si non trouvé
        """
        pass

    @abstractmethod
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[AuthUser]:
        """
        Liste les utilisateurs avec pagination.

        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments
            is_active: Filtrer par statut actif (optionnel)

        Returns:
            Liste d'utilisateurs
        """
        pass

    @abstractmethod
    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """
        Compte le nombre d'utilisateurs.

        Args:
            is_active: Filtrer par statut actif (optionnel)

        Returns:
            Nombre d'utilisateurs
        """
        pass

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """
        Vérifie si un nom d'utilisateur existe.

        Args:
            username: Nom d'utilisateur

        Returns:
            True si existe
        """
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """
        Vérifie si un email existe.

        Args:
            email: Adresse email

        Returns:
            True si existe
        """
        pass
