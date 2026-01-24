"""
Use Case pour la connexion utilisateur.
"""


from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.application.interface.password_hasher import IPasswordHasher
from alak_acl.auth.application.interface.token_service import ITokenService
from alak_acl.auth.domain.dtos.login_dto import LoginDTO
from alak_acl.auth.domain.dtos.token_dto import TokenDTO
from alak_acl.shared.exceptions import InvalidCredentialsError, UserNotActiveError
from alak_acl.shared.logging import logger


class LoginUseCase:
    """
    Use Case pour la connexion d'un utilisateur.

    Gère la logique métier de l'authentification :
    - Vérification des credentials
    - Vérification du statut du compte
    - Génération des tokens JWT

    Attributes:
        auth_repository: Repository pour accéder aux utilisateurs
        token_service: Service pour générer les tokens
        password_hasher: Service pour vérifier les mots de passe
    """

    def __init__(
        self,
        auth_repository: IAuthRepository,
        token_service: ITokenService,
        password_hasher: IPasswordHasher,
    ):
        """
        Initialise le use case.

        Args:
            auth_repository: Repository d'authentification
            token_service: Service de tokens
            password_hasher: Service de hashage
        """
        self._auth_repository = auth_repository
        self._token_service = token_service
        self._password_hasher = password_hasher

    async def execute(self, login_dto: LoginDTO) -> TokenDTO:
        """
        Exécute la connexion d'un utilisateur.

        Args:
            login_dto: DTO contenant username et password

        Returns:
            TokenDTO contenant les tokens d'accès et de rafraîchissement

        Raises:
            InvalidCredentialsError: Si les identifiants sont invalides
            UserNotActiveError: Si le compte est désactivé
        """
        logger.debug(f"Tentative de connexion pour: {login_dto.username}")

        # Récupérer l'utilisateur par username ou email
        user = await self._auth_repository.get_by_username(login_dto.username)
        if not user:
            # Essayer par email
            user = await self._auth_repository.get_by_email(login_dto.username)

        if not user:
            logger.warning(f"Utilisateur non trouvé: {login_dto.username}")
            raise InvalidCredentialsError("Identifiants invalides")

        # Vérifier le mot de passe
        if not self._password_hasher.verify(login_dto.password, user.hashed_password):
            logger.warning(f"Mot de passe incorrect pour: {login_dto.username}")
            raise InvalidCredentialsError("Identifiants invalides")

        # Vérifier si le compte est actif
        if not user.is_active:
            logger.warning(f"Compte désactivé: {login_dto.username}")
            raise UserNotActiveError("Ce compte a été désactivé")

        # Mettre à jour la date de dernière connexion
        user.update_last_login()
        await self._auth_repository.update_user(user)

        # Générer les tokens
        access_token = self._token_service.create_access_token(
            user_id=user.id,
            username=user.username,
            extra_data={
                "email": user.email,
                "is_superuser": user.is_superuser,
                "is_verified": user.is_verified,
            },
        )

        refresh_token = self._token_service.create_refresh_token(
            user_id=user.id,
            username=user.username,
        )

        logger.info(f"Connexion réussie pour: {login_dto.username}")

        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._get_token_expiry(),
        )

    def _get_token_expiry(self) -> int:
        """Retourne la durée de validité du token en secondes."""
        # Par défaut 30 minutes, peut être configuré via le token service
        return 30 * 60
