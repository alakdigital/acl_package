"""
Use Case pour l'inscription utilisateur.
"""

from typing import Optional, TYPE_CHECKING

from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.application.interface.password_hasher import IPasswordHasher
from alak_acl.auth.domain.dtos.register_dto import RegisterDTO
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.shared.exceptions import UserAlreadyExistsError
from alak_acl.shared.logging import logger

if TYPE_CHECKING:
    from alak_acl.roles.application.interface.role_repository import IRoleRepository


class RegisterUseCase:
    """
    Use Case pour l'inscription d'un nouvel utilisateur.

    Gère la logique métier de l'inscription :
    - Vérification de l'unicité username/email
    - Hashage du mot de passe
    - Création de l'utilisateur
    - Assignation du rôle par défaut (si disponible)

    Attributes:
        auth_repository: Repository pour accéder aux utilisateurs
        password_hasher: Service pour hasher les mots de passe
        role_repository: Repository pour gérer les rôles (optionnel)
    """

    def __init__(
        self,
        auth_repository: IAuthRepository,
        password_hasher: IPasswordHasher,
        role_repository: Optional["IRoleRepository"] = None,
    ):
        """
        Initialise le use case.

        Args:
            auth_repository: Repository d'authentification
            password_hasher: Service de hashage
            role_repository: Repository des rôles (optionnel, pour assignation auto)
        """
        self._auth_repository = auth_repository
        self._password_hasher = password_hasher
        self._role_repository = role_repository

    async def execute(self, register_dto: RegisterDTO) -> AuthUser:
        """
        Exécute l'inscription d'un nouvel utilisateur.

        Args:
            register_dto: DTO contenant les informations d'inscription

        Returns:
            Entité AuthUser créée

        Raises:
            UserAlreadyExistsError: Si username ou email existe déjà
        """
        logger.debug(f"Tentative d'inscription pour: {register_dto.username}")

        # Vérifier si le username existe déjà
        if await self._auth_repository.username_exists(register_dto.username):
            logger.warning(f"Username déjà utilisé: {register_dto.username}")
            raise UserAlreadyExistsError(
                "username",
                f"Le nom d'utilisateur '{register_dto.username}' est déjà utilisé"
            )

        # Vérifier si l'email existe déjà
        if await self._auth_repository.email_exists(register_dto.email):
            logger.warning(f"Email déjà utilisé: {register_dto.email}")
            raise UserAlreadyExistsError(
                "email",
                f"L'adresse email '{register_dto.email}' est déjà utilisée"
            )

        # Hasher le mot de passe
        hashed_password = self._password_hasher.hash(register_dto.password)

        # Créer l'entité utilisateur
        # Note: pas de tenant_id car un utilisateur peut appartenir à plusieurs tenants
        # via la table acl_memberships (user_id, tenant_id, role_id)
        user = AuthUser(
            username=register_dto.username,
            email=register_dto.email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,  # Nécessite vérification email
        )

        # Persister l'utilisateur
        created_user = await self._auth_repository.create_user(user)

        logger.info(f"Utilisateur créé avec succès: {register_dto.username}")

        # Assigner le rôle par défaut si disponible
        if self._role_repository:
            await self._assign_default_role(created_user.id)

        return created_user

    async def _assign_default_role(self, user_id: str) -> None:
        """
        Assigne le rôle par défaut à l'utilisateur via membership.

        Le membership est créé avec tenant_id=None pour les rôles globaux.

        Args:
            user_id: ID de l'utilisateur créé
        """
        try:
            default_role = await self._role_repository.get_default_role()
            if default_role:
                await self._role_repository.assign_role_to_user(
                    user_id=user_id,
                    role_id=default_role.id,
                    tenant_id=None,  # Rôle global sans tenant
                )
                logger.debug(f"Rôle par défaut '{default_role.name}' assigné à l'utilisateur {user_id}")
            else:
                logger.debug("Aucun rôle par défaut trouvé")
        except Exception as e:
            # Ne pas bloquer l'inscription si l'assignation échoue
            logger.warning(f"Erreur lors de l'assignation du rôle par défaut: {e}")
