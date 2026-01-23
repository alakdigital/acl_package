from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


class DatabaseConfig:
    def __init__(self, echo: bool = False):
        """
        Classe de configuration de la base de données.
        :param echo: Active ou non les logs SQL.
        """
        self.setting = settings
        self.url = self.setting.database_url
        self.echo = echo
        

        # Création du moteur asynchrone
        self.engine = create_async_engine(
            self.url,
            echo=self.echo,
            future=True,
        )

        # Création de la fabrique de sessions
        self.AsyncSessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Classe de base pour les modèles
        self.Base = declarative_base()

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """Session simple (lecture)."""
        async with self.AsyncSessionLocal() as session:
            yield session

    async def get_db_tx(self) -> AsyncGenerator[AsyncSession, None]:
        """Session avec transaction (POST/PUT/DELETE)."""
        async with self.AsyncSessionLocal() as session:
            async with session.begin():
                yield session


# --- Initialisation globale ---
db_config = DatabaseConfig()

# Aliases pour FastAPI
AsyncDB = Annotated[AsyncSession, Depends(db_config.get_db)]
AsyncDBTx = Annotated[AsyncSession, Depends(db_config.get_db_tx)]
