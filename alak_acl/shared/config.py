"""
Configuration du package fastapi-acl.

Utilise Pydantic Settings pour gérer toute la configuration
via variables d'environnement ou fichier .env.
"""

from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class ACLConfig(BaseSettings):
    """
    Configuration principale du package ACL.

    Toutes les valeurs peuvent être définies via variables d'environnement
    avec le préfixe ACL_ (ex: ACL_DATABASE_TYPE=postgresql).

    Attributes:
        database_type: Type de base de données (mongodb, postgresql, mysql)
        mongodb_uri: URI de connexion MongoDB
        postgresql_uri: URI de connexion PostgreSQL
        mysql_uri: URI de connexion MySQL
        enable_cache: Activer le cache Redis/Memory
        redis_url: URL de connexion Redis
        cache_ttl: Durée de vie du cache en secondes
        cache_backend: Backend de cache (redis, memory)
        jwt_secret_key: Clé secrète pour signer les tokens JWT
        jwt_algorithm: Algorithme de signature JWT
        jwt_access_token_expire_minutes: Durée de vie access token
        jwt_refresh_token_expire_days: Durée de vie refresh token
        enable_api_routes: Activer l'enregistrement automatique des routes
        api_prefix: Préfixe des routes API
        enable_auth_feature: Activer la feature d'authentification
        enable_permissions_feature: Activer la feature des permissions
        enable_roles_feature: Activer la feature des rôles
        disable_auth_for_dev: Désactiver l'auth en développement
        create_default_admin: Créer un admin par défaut au démarrage
        default_admin_username: Nom d'utilisateur admin par défaut
        default_admin_email: Email admin par défaut
        default_admin_password: Mot de passe admin par défaut
        log_level: Niveau de logging
    """

    model_config = SettingsConfigDict(
        env_prefix="ACL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database Configuration
    database_type: Literal["mongodb", "postgresql", "mysql"] = Field(
        default="postgresql",
        description="Type de base de données à utiliser"
    )
    mongodb_uri: Optional[str] = Field(
        default=None,
        description="URI de connexion MongoDB (ex: mongodb://localhost:27017/acl)"
    )
    postgresql_uri: Optional[str] = Field(
        default=None,
        description="URI de connexion PostgreSQL (ex: postgresql+asyncpg://user:pass@localhost/db)"
    )
    mysql_uri: Optional[str] = Field(
        default=None,
        description="URI de connexion MySQL (ex: mysql+asyncmy://user:pass@localhost/db)"
    )

    # Cache Configuration
    enable_cache: bool = Field(
        default=True,
        description="Activer le cache Redis/Memory"
    )
    redis_url: Optional[str] = Field(
        default=None,
        description="URL de connexion Redis (ex: redis://localhost:6379/0)"
    )
    cache_ttl: int = Field(
        default=300,
        description="Durée de vie du cache en secondes"
    )
    cache_backend: Literal["redis", "memory"] = Field(
        default="redis",
        description="Backend de cache à utiliser"
    )

    # JWT Configuration
    jwt_secret_key: str = Field(
        default="change-me-in-production-very-secret-key",
        description="Clé secrète pour signer les tokens JWT"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithme de signature JWT"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        description="Durée de vie du access token en minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        description="Durée de vie du refresh token en jours"
    )

    # Password Reset Configuration
    reset_token_expire_minutes: int = Field(
        default=60,
        description="Durée de vie du token de réinitialisation en minutes"
    )
    password_reset_url: Optional[str] = Field(
        default=None,
        description="URL de la page de réinitialisation du frontend (ex: https://app.com/reset-password)"
    )

    # Email/SMTP Configuration
    smtp_enabled: bool = Field(
        default=False,
        description="Activer l'envoi d'emails via SMTP (sinon utilise Console)"
    )
    smtp_server: Optional[str] = Field(
        default=None,
        description="Serveur SMTP (ex: smtp.gmail.com)"
    )
    smtp_port: int = Field(
        default=587,
        description="Port SMTP (587 pour TLS, 465 pour SSL)"
    )
    smtp_username: Optional[str] = Field(
        default=None,
        description="Nom d'utilisateur SMTP"
    )
    smtp_password: Optional[str] = Field(
        default=None,
        description="Mot de passe SMTP"
    )
    smtp_from_email: Optional[str] = Field(
        default=None,
        description="Adresse email source pour les envois"
    )
    smtp_from_name: str = Field(
        default="alak-acl",
        description="Nom affiché de l'expéditeur"
    )
    smtp_use_tls: bool = Field(
        default=True,
        description="Utiliser STARTTLS (True pour port 587)"
    )

    # API Configuration
    enable_api_routes: bool = Field(
        default=True,
        description="Activer l'enregistrement automatique des routes"
    )
    api_prefix: str = Field(
        default="/api/v1",
        description="Préfixe des routes API"
    )

    # Features Toggle
    enable_auth_feature: bool = Field(
        default=True,
        description="Activer la feature d'authentification"
    )
    enable_permissions_feature: bool = Field(
        default=False,
        description="Activer la feature des permissions"
    )
    enable_roles_feature: bool = Field(
        default=False,
        description="Activer la feature des rôles"
    )
    enable_public_registration: bool = Field(
        default=False,
        description=(
            "Activer l'API publique d'inscription (/register). "
            "True: apps classiques où les utilisateurs s'inscrivent eux-mêmes. "
            "False: SaaS multi-tenant et apps B2B où l'app gère l'inscription via ACLManager.create_account()."
        )
    )

    # Development Configuration
    disable_auth_for_dev: bool = Field(
        default=False,
        description="Désactiver l'authentification en mode développement"
    )
    create_default_admin: bool = Field(
        default=False,
        description="Créer un administrateur par défaut au démarrage"
    )
    default_admin_username: str = Field(
        default="admin",
        description="Nom d'utilisateur de l'admin par défaut"
    )
    default_admin_email: str = Field(
        default="admin@example.com",
        description="Email de l'admin par défaut"
    )
    default_admin_password: str = Field(
        default="admin123",
        description="Mot de passe de l'admin par défaut (à changer!)"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Niveau de logging"
    )

    # Custom Model Configuration
    users_table_name: str = Field(
        default="acl_auth_users",
        description="Nom de la table/collection pour les utilisateurs"
    )
    extra_user_indexes: Optional[str] = Field(
        default=None,
        description="Liste des champs personnalisés à indexer (séparés par des virgules)"
    )

    def get_extra_indexes_list(self) -> list:
        """
        Retourne la liste des champs personnalisés à indexer.

        Returns:
            Liste des noms de champs
        """
        if not self.extra_user_indexes:
            return []
        return [idx.strip() for idx in self.extra_user_indexes.split(",") if idx.strip()]

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Valide que la clé secrète JWT est suffisamment longue."""
        if len(v) < 32:
            raise ValueError("jwt_secret_key doit faire au moins 32 caractères")
        return v

    def get_database_uri(self) -> str:
        """
        Retourne l'URI de la base de données configurée.

        Returns:
            URI de connexion à la base de données

        Raises:
            ValueError: Si l'URI n'est pas configurée pour le type de DB choisi
        """
        uri_map = {
            "mongodb": self.mongodb_uri,
            "postgresql": self.postgresql_uri,
            "mysql": self.mysql_uri,
        }
        uri = uri_map.get(self.database_type)
        if not uri:
            raise ValueError(
                f"URI non configurée pour {self.database_type}. "
                f"Définissez {self.database_type}_uri."
            )
        return uri
