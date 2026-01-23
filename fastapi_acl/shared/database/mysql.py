"""
Connexion MySQL asynchrone avec SQLAlchemy 2.0 et aiomysql.
"""

from typing import Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy import text

from .base import BaseDatabase
from .postgresql import Base  # Réutilise la même Base
from ..exceptions import DatabaseConnectionError
from ..logging import logger


class MySQLDatabase(BaseDatabase):
    """
    Implémentation de la connexion MySQL avec SQLAlchemy async.

    Utilise aiomysql comme driver asynchrone.

    Attributes:
        uri: URI de connexion MySQL
        engine: Moteur SQLAlchemy async
        session_factory: Factory pour créer des sessions
    """

    def __init__(self, uri: str, echo: bool = False):
        """
        Initialise la connexion MySQL.

        Args:
            uri: URI de connexion (ex: mysql+asyncmy://user:pass@localhost/db)
            echo: Activer le logging SQL
        """
        self.uri = uri
        self._echo = echo
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def connect(self) -> None:
        """
        Établit la connexion à MySQL.

        Raises:
            DatabaseConnectionError: Si la connexion échoue
        """
        try:
            logger.info("Connexion à MySQL...")

            self._engine = create_async_engine(
                self.uri,
                echo=self._echo,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )

            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            # Test de la connexion
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info("Connexion MySQL établie avec succès")

        except Exception as e:
            logger.error(f"Erreur de connexion MySQL: {e}")
            raise DatabaseConnectionError(f"Impossible de se connecter à MySQL: {e}")

    async def disconnect(self) -> None:
        """Ferme la connexion MySQL."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Connexion MySQL fermée")

    async def is_connected(self) -> bool:
        """Vérifie si la connexion est active."""
        if not self._engine:
            return False
        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def get_session(self) -> async_sessionmaker[AsyncSession]:
        """
        Retourne la factory de sessions.

        Returns:
            Session factory SQLAlchemy

        Raises:
            DatabaseConnectionError: Si non connecté
        """
        if not self._session_factory:
            raise DatabaseConnectionError("Non connecté à MySQL")
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager pour obtenir une session.

        Usage:
            async with db.session() as session:
                result = await session.execute(query)

        Yields:
            Session SQLAlchemy
        """
        if not self._session_factory:
            raise DatabaseConnectionError("Non connecté à MySQL")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @property
    def engine(self) -> AsyncEngine:
        """Retourne le moteur SQLAlchemy."""
        if not self._engine:
            raise DatabaseConnectionError("Non connecté à MySQL")
        return self._engine

    @property
    def db_type(self) -> str:
        """Retourne 'mysql'."""
        return "mysql"

    async def create_tables(self) -> None:
        """
        Crée toutes les tables définies dans les modèles.

        À utiliser uniquement en développement.
        En production, utiliser Alembic.
        """
        if not self._engine:
            raise DatabaseConnectionError("Non connecté à MySQL")

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables MySQL créées")

    async def drop_tables(self) -> None:
        """
        Supprime toutes les tables.

        ATTENTION: À utiliser uniquement en développement/tests!
        """
        if not self._engine:
            raise DatabaseConnectionError("Non connecté à MySQL")

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Tables MySQL supprimées")
