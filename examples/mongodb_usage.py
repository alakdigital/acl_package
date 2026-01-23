"""
Exemple d'utilisation de fastapi-acl avec MongoDB.

Cet exemple montre comment configurer le package
pour utiliser MongoDB comme base de données.
"""

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from fastapi_acl import (
    ACLManager,
    ACLConfig,
    AuthUser,
    get_current_user,
    get_current_superuser,
)


# Configuration MongoDB
config = ACLConfig(
    # Base de données MongoDB
    database_type="mongodb",
    mongodb_uri="mongodb://localhost:27017/acl_db",

    # Cache (optionnel, fallback vers mémoire si Redis indisponible)
    enable_cache=True,
    cache_backend="memory",  # ou "redis" avec redis_url
    cache_ttl=300,

    # JWT
    jwt_secret_key="ma-cle-secrete-mongodb-minimum-32-caracteres",
    jwt_access_token_expire_minutes=60,

    # API
    enable_api_routes=True,
    api_prefix="/api/v1",

    # Features
    enable_auth_feature=True,

    # Développement
    create_default_admin=True,
    log_level="DEBUG",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    await acl.initialize()
    yield
    await acl.close()


app = FastAPI(
    title="Application MongoDB",
    description="Application avec authentification ACL et MongoDB",
    version="1.0.0",
    lifespan=lifespan,
)

acl = ACLManager(config, app=app)


# ============================================
# Routes d'exemple
# ============================================


@app.get("/admin/dashboard")
async def admin_dashboard(admin: AuthUser = Depends(get_current_superuser)):
    """
    Tableau de bord administrateur.

    Nécessite d'être connecté en tant que superuser.
    """
    # Accès direct aux services via le manager
    repo = acl.get_auth_repository()
    total_users = await repo.count_users()
    active_users = await repo.count_users(is_active=True)

    return {
        "message": f"Bienvenue administrateur {admin.username}",
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
        }
    }


@app.get("/profile")
async def get_profile(user: AuthUser = Depends(get_current_user)):
    """Profil utilisateur."""
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at.isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
