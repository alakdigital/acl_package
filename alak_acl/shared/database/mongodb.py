"""
Connexion MongoDB asynchrone avec motor.
"""

from typing import Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .base import BaseDatabase
from ..exceptions import DatabaseConnectionError
from ..logging import logger


class MongoDBDatabase(BaseDatabase):
    def __init__(self, uri: str, database_name: Optional[str] = None):
        self.uri = uri
        self._database_name = database_name or self._extract_db_name(uri)
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    def _extract_db_name(self, uri: str) -> str:
        if "/" in uri.split("://")[-1]:
            parts = uri.split("/")
            db_part = parts[-1].split("?")[0]
            if db_part:
                return db_part
        return "acl_db"

    async def connect(self) -> None:
        try:
            logger.info(f"Connexion à MongoDB: {self._database_name}")
            self._client = AsyncIOMotorClient(self.uri)
            self._db = self._client[self._database_name]

            await self._client.admin.command("ping")
            logger.info("Connexion MongoDB établie avec succès")

        except Exception as e:
            logger.error(f"Erreur de connexion MongoDB: {e}")
            raise DatabaseConnectionError(f"Impossible de se connecter à MongoDB: {e}")

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Connexion MongoDB fermée")

    async def is_connected(self) -> bool:
        if self._client is None:
            return False
        try:
            await self._client.admin.command("ping")
            return True
        except Exception:
            return False

    def get_session(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise DatabaseConnectionError("Non connecté à MongoDB")
        return self._db

    @property
    def client(self) -> AsyncIOMotorClient:
        if self._client is None:
            raise DatabaseConnectionError("Non connecté à MongoDB")
        return self._client

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self.get_session()

    @property
    def db_type(self) -> str:
        return "mongodb"

    def get_collection(self, name: str) -> Any:
        return self.db[name]
