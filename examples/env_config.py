"""
Exemple d'utilisation de fastapi-acl avec configuration par variables d'environnement.

Toute la configuration peut être définie via des variables d'environnement
avec le préfixe ACL_ ou via un fichier .env.
"""

import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from alak_acl import ACLManager, ACLConfig


# La configuration est automatiquement chargée depuis:
# 1. Les variables d'environnement (préfixe ACL_)
# 2. Le fichier .env dans le répertoire courant

# Exemple de définition manuelle (optionnel):
# os.environ["ACL_DATABASE_TYPE"] = "postgresql"
# os.environ["ACL_POSTGRESQL_URI"] = "postgresql+asyncpg://user:pass@localhost/db"
# os.environ["ACL_JWT_SECRET_KEY"] = "ma-cle-secrete-super-longue-32-chars"

# Création de la config - charge automatiquement depuis l'environnement
config = ACLConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie."""
    await acl.initialize()
    yield
    await acl.close()


app = FastAPI(
    title="Application avec config env",
    lifespan=lifespan,
)

acl = ACLManager(config, app=app)


@app.get("/config")
async def show_config():
    """Affiche la configuration actuelle (pour debug)."""
    return {
        "database_type": config.database_type,
        "cache_enabled": config.enable_cache,
        "cache_backend": config.cache_backend,
        "api_prefix": config.api_prefix,
        "auth_feature": config.enable_auth_feature,
        "log_level": config.log_level,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
