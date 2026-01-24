"""
Factory pour créer les connexions base de données.
"""

from typing import TYPE_CHECKING, Union

from alak_acl.shared.config import ACLConfig
from alak_acl.shared.exceptions import ConfigurationError
from alak_acl.shared.logging import logger

if TYPE_CHECKING:
    from alak_acl.shared.database.mongodb import MongoDBDatabase
    from alak_acl.shared.database.postgresql import PostgreSQLDatabase
    from alak_acl.shared.database.mysql import MySQLDatabase

DatabaseType = Union["MongoDBDatabase", "PostgreSQLDatabase", "MySQLDatabase"]


class DatabaseFactory:
    @staticmethod
    def create(config: ACLConfig) -> DatabaseType:
        db_type = config.database_type
        uri = config.get_database_uri()

        logger.info(f"Création de la connexion {db_type}")

        if db_type == "mongodb":
            try:
                from alak_acl.shared.database.mongodb import MongoDBDatabase
            except ModuleNotFoundError as e:
                raise ConfigurationError(
                    "Backend MongoDB non installé. "
                    "Installe l'extra: pip install alak-acl[mongo]"
                ) from e
            return MongoDBDatabase(uri)

        if db_type == "postgresql":
            try:
                from alak_acl.shared.database.postgresql import PostgreSQLDatabase
            except ModuleNotFoundError as e:
                raise ConfigurationError(
                    "Backend PostgreSQL non installé. "
                    "Installe l'extra: pip install alak-acl[postgres]"
                ) from e
            return PostgreSQLDatabase(uri)

        if db_type == "mysql":
            try:
                from alak_acl.shared.database.mysql import MySQLDatabase
            except ModuleNotFoundError as e:
                raise ConfigurationError(
                    "Backend MySQL non installé. "
                    "Installe l'extra: pip install alak-acl[mysql]"
                ) from e
            return MySQLDatabase(uri)

        raise ConfigurationError(f"Type de base de données non supporté: {db_type}")


_database: DatabaseType | None = None


def get_database() -> DatabaseType:
    if _database is None:
        raise ConfigurationError(
            "Base de données non initialisée. Appelez ACLManager.initialize() d'abord."
        )
    return _database


def set_database(db: DatabaseType) -> None:
    global _database
    _database = db
