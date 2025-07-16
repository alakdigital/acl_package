from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
from app.core.common.setting import reload_settings

settings = reload_settings()
class Database:
    def __init__(self):
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
        self.AsyncSessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.Base = declarative_base()

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.AsyncSessionLocal() as session:
            yield session


# ✅ Instancie une DB globale
db = Database()