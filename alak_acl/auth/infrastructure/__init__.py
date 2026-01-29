"""
Couche Infrastructure - Implémentations concrètes.

Contient les modèles DB, mappers, repositories et services.

Les imports sont conditionnels pour éviter de charger des dépendances
non installées (ex: SQLAlchemy pour les utilisateurs MongoDB).
"""

from alak_acl.auth.infrastructure.mappers.auth_user_mapper import AuthUserMapper
from alak_acl.auth.infrastructure.services.argon2_password_hasher import Argon2PasswordHasher
from alak_acl.auth.infrastructure.services.jwt_token_service import JWTTokenService


# Lazy imports pour éviter les erreurs de dépendances manquantes
def __getattr__(name: str):
    """Lazy loading des classes SQL/DB pour éviter les dépendances manquantes."""
    # Modèles MongoDB (nécessite motor/pymongo/bson)
    if name == "MongoAuthUserModel":
        from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel
        return MongoAuthUserModel
    # Modèles SQL (nécessite SQLAlchemy)
    elif name == "SQLAuthUserModel":
        from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel
        return SQLAuthUserModel
    # Repositories
    elif name == "PostgreSQLAuthRepository":
        from alak_acl.auth.infrastructure.repositories.postgresql_repository import PostgreSQLAuthRepository
        return PostgreSQLAuthRepository
    elif name == "MySQLAuthRepository":
        from alak_acl.auth.infrastructure.repositories.mysql_repository import MySQLAuthRepository
        return MySQLAuthRepository
    elif name == "MongoDBAuthRepository":
        from alak_acl.auth.infrastructure.repositories.mongodb_repository import MongoDBAuthRepository
        return MongoDBAuthRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "SQLAuthUserModel",
    "MongoAuthUserModel",
    "AuthUserMapper",
    "PostgreSQLAuthRepository",
    "MongoDBAuthRepository",
    "MySQLAuthRepository",
    "JWTTokenService",
    "Argon2PasswordHasher",
]
