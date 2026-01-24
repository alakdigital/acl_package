"""
Factory pour créer les connexions base de données.
"""

from typing import Union

from alak_acl.shared.database.base import BaseDatabase
from alak_acl.shared.database.mongodb import MongoDBDatabase
from alak_acl.shared.database.postgresql import PostgreSQLDatabase
from alak_acl.shared.database.mysql import MySQLDatabase
from alak_acl.shared.config import ACLConfig
from alak_acl.shared.exceptions import ConfigurationError
from alak_acl.shared.logging import logger


DatabaseType = Union[MongoDBDatabase, PostgreSQLDatabase, MySQLDatabase]


class DatabaseFactory:
    """
    Factory pour créer la connexion base de données appropriée.

    Crée l'instance de database selon le type configuré.
    """

    @staticmethod
    def create(config: ACLConfig) -> DatabaseType:
        """
        Crée une instance de base de données selon la configuration.

        Args:
            config: Configuration ACL

        Returns:
            Instance de base de données (MongoDB, PostgreSQL ou MySQL)

        Raises:
            ConfigurationError: Si le type de DB n'est pas supporté
        """
        db_type = config.database_type
        uri = config.get_database_uri()

        logger.info(f"Création de la connexion {db_type}")

        if db_type == "mongodb":
            return MongoDBDatabase(uri)
        elif db_type == "postgresql":
            return PostgreSQLDatabase(uri)
        elif db_type == "mysql":
            return MySQLDatabase(uri)
        else:
            raise ConfigurationError(f"Type de base de données non supporté: {db_type}")


# Instance globale (initialisée par ACLManager)
_database: DatabaseType | None = None


def get_database() -> DatabaseType:
    """
    Retourne l'instance globale de la base de données.

    Returns:
        Instance de base de données

    Raises:
        ConfigurationError: Si la DB n'est pas initialisée
    """
    if _database is None:
        raise ConfigurationError(
            "Base de données non initialisée. Appelez ACLManager.initialize() d'abord."
        )
    return _database


def set_database(db: DatabaseType) -> None:
    """
    Définit l'instance globale de la base de données.

    Args:
        db: Instance de base de données
    """
    global _database
    _database = db
