"""
Connexion MongoDB asynchrone avec motor.
"""

from typing import Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .base import BaseDatabase
from ..exceptions import DatabaseConnectionError
from ..logging import logger


class MongoDBDatabase(BaseDatabase):
    """
    Implémentation de la connexion MongoDB avec motor.

    Attributes:
        uri: URI de connexion MongoDB
        database_name: Nom de la base de données
        client: Client motor
        db: Instance de la base de données
    """

    def __init__(self, uri: str, database_name: Optional[str] = None):
        """
        Initialise la connexion MongoDB.

        Args:
            uri: URI de connexion (ex: mongodb://localhost:27017/mydb)
            database_name: Nom de la DB (optionnel si présent dans l'URI)
        """
        self.uri = uri
        self._database_name = database_name or self._extract_db_name(uri)
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    def _extract_db_name(self, uri: str) -> str:
        """Extrait le nom de la DB depuis l'URI."""
        # Format: mongodb://host:port/database_name
        if "/" in uri.split("://")[-1]:
            parts = uri.split("/")
            db_part = parts[-1].split("?")[0]
            if db_part:
                return db_part
        return "acl_db"

    async def connect(self) -> None:
        """
        Établit la connexion à MongoDB.

        Raises:
            DatabaseConnectionError: Si la connexion échoue
        """
        try:
            logger.info(f"Connexion à MongoDB: {self._database_name}")
            self._client = AsyncIOMotorClient(self.uri)
            self._db = self._client[self._database_name]

            # Test de la connexion
            await self._client.admin.command("ping")
            logger.info("Connexion MongoDB établie avec succès")

        except Exception as e:
            logger.error(f"Erreur de connexion MongoDB: {e}")
            raise DatabaseConnectionError(f"Impossible de se connecter à MongoDB: {e}")

    async def disconnect(self) -> None:
        """Ferme la connexion MongoDB."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Connexion MongoDB fermée")

    async def is_connected(self) -> bool:
        """Vérifie si la connexion est active."""
        if not self._client:
            return False
        try:
            await self._client.admin.command("ping")
            return True
        except Exception:
            return False

    def get_session(self) -> AsyncIOMotorDatabase:
        """
        Retourne l'instance de la base de données.

        Returns:
            Base de données MongoDB

        Raises:
            DatabaseConnectionError: Si non connecté
        """
        if not self._db:
            raise DatabaseConnectionError("Non connecté à MongoDB")
        return self._db

    @property
    def client(self) -> AsyncIOMotorClient:
        """Retourne le client motor."""
        if not self._client:
            raise DatabaseConnectionError("Non connecté à MongoDB")
        return self._client

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Alias pour get_session()."""
        return self.get_session()

    @property
    def db_type(self) -> str:
        """Retourne 'mongodb'."""
        return "mongodb"

    def get_collection(self, name: str) -> Any:
        """
        Retourne une collection MongoDB.

        Args:
            name: Nom de la collection

        Returns:
            Collection MongoDB
        """
        return self.db[name]
