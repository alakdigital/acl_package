import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db.postgre.database_mysql import db_config
from app.core.db.redis.cache_manager import redis_cache
from app.core.http_errors import custom_exception, generic_exception, validation_exception
from app.router.router import api_router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Affiche dans la console
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application."""
    # Startup
    logger.info("🚀 Démarrage de l'application...")
     # Initialisation de la base de données
    try:
        async with db_config.engine.begin() as conn:
            await conn.run_sync(db_config.Base.metadata.create_all)
        logging.info("Base de données initialisée")
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de la base de données : {e}")
    
    await redis_cache.connect()
    # await rabbitmq.connect()
    logger.info("✅ Application démarrée avec succès!")

    yield

    # Shutdown
    logger.info("🛑 Arrêt de l'application...")
    await db_config.engine.dispose()
    logging.info("Connexion à la base de données fermée")
    await redis_cache.disconnect()
    logger.info("✅ Application arrêtée")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API complète pour une plateforme de librairies en ligne",
    lifespan=lifespan,
    debug=settings.debug
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(api_router, prefix="/api/v1")

custom_exception(app)
validation_exception(app)
generic_exception(app)


@app.get("/")
async def root():
    """Route racine."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)