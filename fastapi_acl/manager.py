"""
ACLManager - Point d'entrée principal du package fastapi-acl.

Ce module fournit le gestionnaire principal qui initialise
toutes les connexions et enregistre automatiquement les routes.
"""

from typing import Optional, Union

from fastapi import FastAPI

from .shared.config import ACLConfig
from .shared.database.factory import DatabaseFactory, set_database, DatabaseType
from .shared.database.mongodb import MongoDBDatabase
from .shared.database.postgresql import PostgreSQLDatabase
from .shared.database.mysql import MySQLDatabase
from .shared.cache.factory import CacheFactory, set_cache, CacheType
from .shared.exceptions import ConfigurationError
from .shared.logging import logger, get_logger

from .auth.application.interface.auth_repository import IAuthRepository
from .auth.application.interface.token_service import ITokenService
from .auth.application.interface.password_hasher import IPasswordHasher
from .auth.infrastructure.repositories.postgresql_repository import PostgreSQLAuthRepository
from .auth.infrastructure.repositories.mongodb_repository import MongoDBAuthRepository
from .auth.infrastructure.repositories.mysql_repository import MySQLAuthRepository
from .auth.infrastructure.services.jwt_token_service import JWTTokenService
from .auth.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from .auth.interface.dependencies import set_auth_dependencies
from .auth.interface.api import router as auth_router
from .auth.interface.admin.routes import router as admin_router
from .auth.domain.dtos.register_dto import RegisterDTO
from .auth.application.usecases.register_usecase import RegisterUseCase


class ACLManager:
    """
    Gestionnaire principal du package fastapi-acl.

    Point d'entrée unique pour initialiser et configurer
    toute l'infrastructure ACL.

    Attributes:
        config: Configuration ACL
        app: Instance FastAPI (optionnelle)
        database: Connexion base de données
        cache: Backend de cache
        auth_repository: Repository d'authentification
        token_service: Service de tokens JWT
        password_hasher: Service de hashage

    Example:
        ```python
        from fastapi import FastAPI
        from fastapi_acl import ACLManager, ACLConfig

        app = FastAPI()
        config = ACLConfig(
            database_type="postgresql",
            postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
        )

        acl = ACLManager(config, app=app)

        @app.on_event("startup")
        async def startup():
            await acl.initialize()

        @app.on_event("shutdown")
        async def shutdown():
            await acl.close()
        ```
    """

    def __init__(
        self,
        config: ACLConfig,
        app: Optional[FastAPI] = None,
    ):
        """
        Initialise le gestionnaire ACL.

        Args:
            config: Configuration ACL
            app: Instance FastAPI pour l'auto-registration des routes
        """
        self._config = config
        self._app = app
        self._initialized = False

        # Infrastructure (initialisées dans initialize())
        self._database: Optional[DatabaseType] = None
        self._cache: Optional[CacheType] = None

        # Services Auth (initialisés dans initialize())
        self._auth_repository: Optional[IAuthRepository] = None
        self._token_service: Optional[ITokenService] = None
        self._password_hasher: Optional[IPasswordHasher] = None

        # Configurer le logger
        get_logger(level=config.log_level)

        # Auto-register des routes si app fournie
        if app and config.enable_api_routes:
            self._register_routes(app)

    def _register_routes(self, app: FastAPI) -> None:
        """
        Enregistre automatiquement les routes dans FastAPI.

        Args:
            app: Instance FastAPI
        """
        prefix = self._config.api_prefix

        if self._config.enable_auth_feature:
            app.include_router(auth_router, prefix=prefix)
            app.include_router(admin_router, prefix=prefix)
            logger.info(f"Routes auth enregistrées avec préfixe: {prefix}")

        # Futures features
        if self._config.enable_permissions_feature:
            logger.warning("Feature permissions non encore implémentée")

        if self._config.enable_roles_feature:
            logger.warning("Feature roles non encore implémentée")

    async def initialize(self) -> None:
        """
        Initialise toutes les connexions et services.

        Cette méthode doit être appelée au démarrage de l'application,
        typiquement dans l'événement startup de FastAPI.

        Raises:
            ConfigurationError: Si l'initialisation échoue
        """
        if self._initialized:
            logger.warning("ACLManager déjà initialisé")
            return

        logger.info("Initialisation de ACLManager...")

        try:
            # 1. Initialiser la base de données
            await self._init_database()

            # 2. Initialiser le cache
            await self._init_cache()

            # 3. Initialiser les services Auth
            if self._config.enable_auth_feature:
                await self._init_auth_services()

            # 4. Créer l'admin par défaut si configuré
            if self._config.create_default_admin:
                await self._create_default_admin()

            self._initialized = True
            logger.info("ACLManager initialisé avec succès")

        except Exception as e:
            logger.error(f"Erreur d'initialisation: {e}")
            await self.close()
            raise ConfigurationError(f"Échec de l'initialisation: {e}")

    async def _init_database(self) -> None:
        """Initialise la connexion à la base de données."""
        self._database = DatabaseFactory.create(self._config)
        await self._database.connect()
        set_database(self._database)

        # Créer les tables si PostgreSQL/MySQL
        if isinstance(self._database, (PostgreSQLDatabase, MySQLDatabase)):
            await self._database.create_tables()

    async def _init_cache(self) -> None:
        """Initialise le cache."""
        self._cache = await CacheFactory.create(self._config)
        set_cache(self._cache)

    async def _init_auth_services(self) -> None:
        """Initialise les services d'authentification."""
        # Password hasher
        self._password_hasher = BcryptPasswordHasher()

        # Token service
        self._token_service = JWTTokenService(self._config)

        # Repository selon le type de DB
        if isinstance(self._database, MongoDBDatabase):
            self._auth_repository = MongoDBAuthRepository(self._database)
            # Créer les index MongoDB
            await self._auth_repository.create_indexes()
        elif isinstance(self._database, PostgreSQLDatabase):
            self._auth_repository = PostgreSQLAuthRepository(self._database)
        elif isinstance(self._database, MySQLDatabase):
            self._auth_repository = MySQLAuthRepository(self._database)

        # Configurer les dépendances FastAPI
        set_auth_dependencies(
            auth_repository=self._auth_repository,
            token_service=self._token_service,
            password_hasher=self._password_hasher,
        )

        logger.info("Services d'authentification initialisés")

    async def _create_default_admin(self) -> None:
        """Crée l'administrateur par défaut si configuré."""
        if not self._auth_repository or not self._password_hasher:
            return

        # Vérifier si l'admin existe déjà
        existing = await self._auth_repository.get_by_username(
            self._config.default_admin_username
        )
        if existing:
            logger.debug("Admin par défaut existe déjà")
            return

        try:
            register_dto = RegisterDTO(
                username=self._config.default_admin_username,
                email=self._config.default_admin_email,
                password=self._config.default_admin_password,
            )

            register_usecase = RegisterUseCase(
                auth_repository=self._auth_repository,
                password_hasher=self._password_hasher,
            )

            user = await register_usecase.execute(register_dto)

            # Promouvoir en superuser
            user.is_superuser = True
            user.is_verified = True
            await self._auth_repository.update_user(user)

            logger.info(f"Admin par défaut créé: {self._config.default_admin_username}")

        except Exception as e:
            logger.warning(f"Impossible de créer l'admin par défaut: {e}")

    async def close(self) -> None:
        """
        Ferme toutes les connexions.

        Cette méthode doit être appelée à l'arrêt de l'application,
        typiquement dans l'événement shutdown de FastAPI.
        """
        logger.info("Fermeture de ACLManager...")

        if self._cache:
            await self._cache.disconnect()

        if self._database:
            await self._database.disconnect()

        self._initialized = False
        logger.info("ACLManager fermé")

    # ============================================
    # Getters publics
    # ============================================

    @property
    def config(self) -> ACLConfig:
        """Retourne la configuration."""
        return self._config

    @property
    def is_initialized(self) -> bool:
        """Retourne True si le manager est initialisé."""
        return self._initialized

    def get_auth_repository(self) -> IAuthRepository:
        """
        Retourne le repository d'authentification.

        Returns:
            Repository d'authentification

        Raises:
            ConfigurationError: Si non initialisé
        """
        if not self._auth_repository:
            raise ConfigurationError("Auth repository non initialisé")
        return self._auth_repository

    def get_token_service(self) -> ITokenService:
        """
        Retourne le service de tokens.

        Returns:
            Service de tokens

        Raises:
            ConfigurationError: Si non initialisé
        """
        if not self._token_service:
            raise ConfigurationError("Token service non initialisé")
        return self._token_service

    def get_password_hasher(self) -> IPasswordHasher:
        """
        Retourne le service de hashage.

        Returns:
            Service de hashage

        Raises:
            ConfigurationError: Si non initialisé
        """
        if not self._password_hasher:
            raise ConfigurationError("Password hasher non initialisé")
        return self._password_hasher

    def get_database(self) -> DatabaseType:
        """
        Retourne la connexion base de données.

        Returns:
            Connexion DB

        Raises:
            ConfigurationError: Si non initialisé
        """
        if not self._database:
            raise ConfigurationError("Database non initialisée")
        return self._database

    def get_cache(self) -> CacheType:
        """
        Retourne le backend de cache.

        Returns:
            Backend de cache

        Raises:
            ConfigurationError: Si non initialisé
        """
        if not self._cache:
            raise ConfigurationError("Cache non initialisé")
        return self._cache
