"""
Use Case pour l'inscription utilisateur.
"""


from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.application.interface.password_hasher import IPasswordHasher
from alak_acl.auth.domain.dtos.register_dto import RegisterDTO
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.shared.exceptions import UserAlreadyExistsError
from alak_acl.shared.logging import logger


class RegisterUseCase:
    """
    Use Case pour l'inscription d'un nouvel utilisateur.

    Gère la logique métier de l'inscription :
    - Vérification de l'unicité username/email
    - Hashage du mot de passe
    - Création de l'utilisateur

    Attributes:
        auth_repository: Repository pour accéder aux utilisateurs
        password_hasher: Service pour hasher les mots de passe
    """

    def __init__(
        self,
        auth_repository: IAuthRepository,
        password_hasher: IPasswordHasher,
    ):
        """
        Initialise le use case.

        Args:
            auth_repository: Repository d'authentification
            password_hasher: Service de hashage
        """
        self._auth_repository = auth_repository
        self._password_hasher = password_hasher

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

        return created_user
