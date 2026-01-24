"""
Exemple d'utilisation basique de fastapi-acl.

Cet exemple montre comment configurer et utiliser le package
avec PostgreSQL et Redis.
"""

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from alak_acl import (
    ACLManager,
    ACLConfig,
    AuthUser,
    get_current_user,
    get_current_active_user,
)


# Configuration
config = ACLConfig(
    # Base de données
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://postgres:password@localhost:5432/acl_db",

    # Cache
    enable_cache=True,
    redis_url="redis://localhost:6379/0",
    cache_ttl=300,

    # JWT
    jwt_secret_key="votre-cle-secrete-de-minimum-32-caracteres-ici",
    jwt_access_token_expire_minutes=30,
    jwt_refresh_token_expire_days=7,

    # API
    enable_api_routes=True,
    api_prefix="/api/v1",

    # Features
    enable_auth_feature=True,

    # Développement
    create_default_admin=True,
    default_admin_username="admin",
    default_admin_email="admin@example.com",
    default_admin_password="adminpassword123",
    log_level="INFO",
)


# Création de l'application avec lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    await acl.initialize()
    yield
    # Shutdown
    await acl.close()


app = FastAPI(
    title="Mon Application",
    description="Application avec authentification ACL",
    version="1.0.0",
    lifespan=lifespan,
)

# Initialisation du manager ACL
# Les routes sont automatiquement enregistrées!
acl = ACLManager(config, app=app)


# ============================================
# Routes protégées personnalisées
# ============================================


@app.get("/protected")
async def protected_route(current_user: AuthUser = Depends(get_current_active_user)):
    """
    Route protégée nécessitant une authentification.

    L'utilisateur doit être connecté et actif.
    """
    return {
        "message": f"Bienvenue {current_user.username}!",
        "user_id": str(current_user.id),
        "email": current_user.email,
    }


@app.get("/public")
async def public_route():
    """Route publique accessible sans authentification."""
    return {"message": "Cette route est publique"}


# ============================================
# Point d'entrée
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
