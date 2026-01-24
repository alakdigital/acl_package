"""
ACLManager - Point d'entrée principal du package fastapi-acl.

Ce module fournit le gestionnaire principal qui initialise
toutes les connexions et enregistre automatiquement les routes.

Supporte les modèles utilisateur personnalisés pour ajouter
des champs/colonnes supplémentaires.
"""

from typing import Optional, Union, Type, List

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
from .auth.infrastructure.models.sql_model import SQLAuthUserModel
from .auth.infrastructure.models.mongo_model import MongoAuthUserModel
from .auth.infrastructure.mappers.auth_user_mapper import AuthUserMapper
from .auth.interface.dependencies import set_auth_dependencies
from .auth.interface.api import router as auth_router
from .auth.interface.admin.routes import router as admin_router
from .auth.domain.dtos.register_dto import RegisterDTO
from .auth.application.usecases.register_usecase import RegisterUseCase

# Roles imports
from .roles.application.interface.role_repository import IRoleRepository
from .roles.infrastructure.repositories.postgresql_repository import PostgreSQLRoleRepository
from .roles.infrastructure.repositories.mongodb_repository import MongoDBRoleRepository
from .roles.infrastructure.repositories.mysql_repository import MySQLRoleRepository
from .roles.interface.dependencies import set_role_dependencies
from .roles.interface.routes import router as roles_router
from .roles.domain.entities.role import Role

# Permissions imports
from .permissions.application.interface.permission_repository import IPermissionRepository
from .permissions.infrastructure.repositories.postgresql_repository import PostgreSQLPermissionRepository
from .permissions.infrastructure.repositories.mongodb_repository import MongoDBPermissionRepository
from .permissions.infrastructure.repositories.mysql_repository import MySQLPermissionRepository
from .permissions.interface.dependencies import set_permission_dependencies
from .permissions.interface.routes import router as permissions_router
from .permissions.domain.entities.permission import Permission


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

    Example avec modèle personnalisé:
        ```python
        from sqlalchemy import Column, String, Integer
        from fastapi_acl import ACLManager, ACLConfig
        from fastapi_acl.auth.infrastructure.models import SQLAuthUserModel

        # Définir un modèle personnalisé avec des colonnes supplémentaires
        class CustomUserModel(SQLAuthUserModel):
            __tablename__ = "users"
            phone = Column(String(20), nullable=True)
            company = Column(String(100), nullable=True)

        acl = ACLManager(
            config=config,
            app=app,
            sql_user_model=CustomUserModel,
        )
        ```
    """

    def __init__(
        self,
        config: ACLConfig,
        app: Optional[FastAPI] = None,
        sql_user_model: Optional[Type[SQLAuthUserModel]] = None,
        mongo_user_model: Optional[Type[MongoAuthUserModel]] = None,
        extra_user_indexes: Optional[List[str]] = None,
    ):
        """
        Initialise le gestionnaire ACL.

        Args:
            config: Configuration ACL
            app: Instance FastAPI pour l'auto-registration des routes
            sql_user_model: Classe de modèle SQL personnalisée (pour PostgreSQL/MySQL)
            mongo_user_model: Classe de modèle MongoDB personnalisée
            extra_user_indexes: Liste des champs personnalisés à indexer (MongoDB)
        """
        self._config = config
        self._app = app
        self._initialized = False

        # Modèles personnalisés
        self._sql_user_model = sql_user_model or SQLAuthUserModel
        self._mongo_user_model = mongo_user_model or MongoAuthUserModel
        self._extra_user_indexes = extra_user_indexes or self._parse_extra_indexes()

        # Infrastructure (initialisées dans initialize())
        self._database: Optional[DatabaseType] = None
        self._cache: Optional[CacheType] = None

        # Services Auth (initialisés dans initialize())
        self._auth_repository: Optional[IAuthRepository] = None
        self._token_service: Optional[ITokenService] = None
        self._password_hasher: Optional[IPasswordHasher] = None

        # Services Roles (initialisés dans initialize())
        self._role_repository: Optional[IRoleRepository] = None

        # Services Permissions (initialisés dans initialize())
        self._permission_repository: Optional[IPermissionRepository] = None

        # Configurer le logger
        get_logger(level=config.log_level)

        # Auto-register des routes si app fournie
        if app and config.enable_api_routes:
            self._register_routes(app)

    def _parse_extra_indexes(self) -> List[str]:
        """Parse les index supplémentaires depuis la config."""
        if self._config.extra_user_indexes:
            return [
                idx.strip()
                for idx in self._config.extra_user_indexes.split(",")
                if idx.strip()
            ]
        return []

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

        # Feature roles
        if self._config.enable_roles_feature:
            app.include_router(roles_router, prefix=prefix)
            logger.info(f"Routes roles enregistrées avec préfixe: {prefix}")

        # Feature permissions
        if self._config.enable_permissions_feature:
            app.include_router(permissions_router, prefix=prefix)
            logger.info(f"Routes permissions enregistrées avec préfixe: {prefix}")

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

            # 4. Initialiser les services Roles
            if self._config.enable_roles_feature:
                await self._init_role_services()

            # 5. Créer l'admin par défaut si configuré
            if self._config.create_default_admin:
                await self._create_default_admin()

            # 6. Créer les rôles par défaut si configurés
            if self._config.enable_roles_feature:
                await self._create_default_roles()

            # 7. Initialiser les services Permissions
            if self._config.enable_permissions_feature:
                await self._init_permission_services()

            # 8. Créer les permissions par défaut
            if self._config.enable_permissions_feature:
                await self._create_default_permissions()

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
        """
        Initialise les services d'authentification.

        Utilise les modèles personnalisés si fournis.
        """
        # Password hasher
        self._password_hasher = BcryptPasswordHasher()

        # Token service
        self._token_service = JWTTokenService(self._config)

        # Créer le mapper avec les modèles personnalisés
        mapper = AuthUserMapper(
            sql_model_class=self._sql_user_model,
            mongo_model_class=self._mongo_user_model,
        )

        # Repository selon le type de DB avec modèle personnalisé
        if isinstance(self._database, MongoDBDatabase):
            collection_name = self._config.users_table_name or "auth_users"
            self._auth_repository = MongoDBAuthRepository(
                db=self._database,
                collection_name=collection_name,
                model_class=self._mongo_user_model,
                mapper=mapper,
            )
            # Créer les index MongoDB (avec les index personnalisés)
            await self._auth_repository.create_indexes(
                extra_indexes=self._extra_user_indexes
            )
            logger.debug(f"MongoDB collection: {collection_name}")

        elif isinstance(self._database, PostgreSQLDatabase):
            self._auth_repository = PostgreSQLAuthRepository(
                db=self._database,
                model_class=self._sql_user_model,
                mapper=mapper,
            )
            logger.debug(f"PostgreSQL model: {self._sql_user_model.__name__}")

        elif isinstance(self._database, MySQLDatabase):
            self._auth_repository = MySQLAuthRepository(
                db=self._database,
                model_class=self._sql_user_model,
                mapper=mapper,
            )
            logger.debug(f"MySQL model: {self._sql_user_model.__name__}")

        # Configurer les dépendances FastAPI
        set_auth_dependencies(
            auth_repository=self._auth_repository,
            token_service=self._token_service,
            password_hasher=self._password_hasher,
        )

        logger.info("Services d'authentification initialisés")

    async def _init_role_services(self) -> None:
        """
        Initialise les services de gestion des rôles.
        """
        # Repository selon le type de DB
        if isinstance(self._database, MongoDBDatabase):
            self._role_repository = MongoDBRoleRepository(
                db=self._database,
                roles_collection="acl_roles",
                user_roles_collection="acl_user_roles",
            )
            # Créer les index MongoDB
            await self._role_repository.create_indexes()
            logger.debug("MongoDB role repository initialisé")

        elif isinstance(self._database, PostgreSQLDatabase):
            self._role_repository = PostgreSQLRoleRepository(
                db=self._database,
            )
            logger.debug("PostgreSQL role repository initialisé")

        elif isinstance(self._database, MySQLDatabase):
            self._role_repository = MySQLRoleRepository(
                db=self._database,
            )
            logger.debug("MySQL role repository initialisé")

        # Configurer les dépendances FastAPI
        set_role_dependencies(
            role_repository=self._role_repository,
        )

        logger.info("Services de rôles initialisés")

    async def _init_permission_services(self) -> None:
        """
        Initialise les services de gestion des permissions.
        """
        # Repository selon le type de DB
        if isinstance(self._database, MongoDBDatabase):
            self._permission_repository = MongoDBPermissionRepository(
                db=self._database,
                collection_name="acl_permissions",
            )
            # Créer les index MongoDB
            await self._permission_repository.create_indexes()
            logger.debug("MongoDB permission repository initialisé")

        elif isinstance(self._database, PostgreSQLDatabase):
            self._permission_repository = PostgreSQLPermissionRepository(
                db=self._database,
            )
            logger.debug("PostgreSQL permission repository initialisé")

        elif isinstance(self._database, MySQLDatabase):
            self._permission_repository = MySQLPermissionRepository(
                db=self._database,
            )
            logger.debug("MySQL permission repository initialisé")

        # Configurer les dépendances FastAPI
        set_permission_dependencies(
            permission_repository=self._permission_repository,
        )

        logger.info("Services de permissions initialisés")

    async def _create_default_permissions(self) -> None:
        """
        Crée les permissions par défaut si elles n'existent pas.
        """
        if not self._permission_repository:
            return

        default_permissions = [
            # Permissions profile
            Permission(
                resource="profile",
                action="read",
                display_name="Voir son profil",
                description="Permet de consulter son propre profil",
                category="User",
                is_system=True,
            ),
            Permission(
                resource="profile",
                action="update",
                display_name="Modifier son profil",
                description="Permet de modifier son propre profil",
                category="User",
                is_system=True,
            ),
            # Permissions users (admin)
            Permission(
                resource="users",
                action="read",
                display_name="Voir les utilisateurs",
                description="Permet de consulter la liste des utilisateurs",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="users",
                action="create",
                display_name="Créer des utilisateurs",
                description="Permet de créer de nouveaux utilisateurs",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="users",
                action="update",
                display_name="Modifier les utilisateurs",
                description="Permet de modifier les utilisateurs",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="users",
                action="delete",
                display_name="Supprimer des utilisateurs",
                description="Permet de supprimer des utilisateurs",
                category="Admin",
                is_system=True,
            ),
            # Permissions roles (admin)
            Permission(
                resource="roles",
                action="read",
                display_name="Voir les rôles",
                description="Permet de consulter les rôles",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="roles",
                action="create",
                display_name="Créer des rôles",
                description="Permet de créer de nouveaux rôles",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="roles",
                action="update",
                display_name="Modifier les rôles",
                description="Permet de modifier les rôles",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="roles",
                action="delete",
                display_name="Supprimer des rôles",
                description="Permet de supprimer des rôles",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="roles",
                action="assign",
                display_name="Assigner des rôles",
                description="Permet d'assigner des rôles aux utilisateurs",
                category="Admin",
                is_system=True,
            ),
            # Permissions système
            Permission(
                resource="permissions",
                action="read",
                display_name="Voir les permissions",
                description="Permet de consulter les permissions",
                category="Admin",
                is_system=True,
            ),
            Permission(
                resource="permissions",
                action="manage",
                display_name="Gérer les permissions",
                description="Permet de créer/modifier/supprimer les permissions",
                category="Admin",
                is_system=True,
            ),
        ]

        created_count = 0
        for permission in default_permissions:
            exists = await self._permission_repository.permission_exists(permission.name)
            if not exists:
                try:
                    await self._permission_repository.create_permission(permission)
                    created_count += 1
                except Exception as e:
                    logger.warning(
                        f"Impossible de créer la permission {permission.name}: {e}"
                    )

        if created_count > 0:
            logger.info(f"{created_count} permissions par défaut créées")

    async def _create_default_roles(self) -> None:
        """
        Crée les rôles par défaut (admin, user) si ils n'existent pas.
        """
        if not self._role_repository:
            return

        default_roles = [
            Role(
                name="admin",
                display_name="Administrateur",
                description="Rôle administrateur avec tous les droits",
                permissions=["*"],
                is_system=True,
                is_default=False,
                priority=100,
            ),
            Role(
                name="user",
                display_name="Utilisateur",
                description="Rôle utilisateur standard",
                permissions=["profile:read", "profile:update"],
                is_system=True,
                is_default=True,
                priority=1,
            ),
        ]

        for role in default_roles:
            existing = await self._role_repository.get_by_name(role.name)
            if not existing:
                try:
                    await self._role_repository.create_role(role)
                    logger.info(f"Rôle par défaut créé: {role.name}")
                except Exception as e:
                    logger.warning(f"Impossible de créer le rôle {role.name}: {e}")
            else:
                logger.debug(f"Rôle {role.name} existe déjà")

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

            # Assigner le rôle admin si la feature roles est activée
            if self._role_repository and self._config.enable_roles_feature:
                admin_role = await self._role_repository.get_by_name("admin")
                if admin_role:
                    await self._role_repository.assign_role_to_user(
                        user_id=user.id,
                        role_id=admin_role.id,
                    )
                    logger.debug(f"Rôle admin assigné à {user.username}")

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

    def get_role_repository(self) -> IRoleRepository:
        """
        Retourne le repository des rôles.

        Returns:
            Repository des rôles

        Raises:
            ConfigurationError: Si non initialisé ou feature désactivée
        """
        if not self._role_repository:
            raise ConfigurationError(
                "Role repository non initialisé. "
                "Vérifiez que enable_roles_feature=True"
            )
        return self._role_repository

    def get_permission_repository(self) -> IPermissionRepository:
        """
        Retourne le repository des permissions.

        Returns:
            Repository des permissions

        Raises:
            ConfigurationError: Si non initialisé ou feature désactivée
        """
        if not self._permission_repository:
            raise ConfigurationError(
                "Permission repository non initialisé. "
                "Vérifiez que enable_permissions_feature=True"
            )
        return self._permission_repository
