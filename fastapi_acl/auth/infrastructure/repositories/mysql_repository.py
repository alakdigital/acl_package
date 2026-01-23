"""
Repository MySQL pour l'authentification.

Réutilise l'implémentation PostgreSQL car les deux utilisent SQLAlchemy.
"""

from ....shared.database.mysql import MySQLDatabase
from .postgresql_repository import PostgreSQLAuthRepository


class MySQLAuthRepository(PostgreSQLAuthRepository):
    """
    Implémentation du repository d'authentification pour MySQL.

    Hérite de PostgreSQLAuthRepository car les deux utilisent SQLAlchemy
    avec la même syntaxe.

    Attributes:
        db: Instance de connexion MySQL
    """

    def __init__(self, db: MySQLDatabase):
        """
        Initialise le repository.

        Args:
            db: Instance de MySQLDatabase
        """
        # MySQLDatabase a la même interface que PostgreSQLDatabase
        super().__init__(db)  # type: ignore
