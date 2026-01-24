# FastAPI-ACL

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Package professionnel de gestion ACL (Access Control List) pour FastAPI.**

Gérez l'authentification, les rôles et les permissions dans vos applications FastAPI en quelques lignes de code.

## Caractéristiques

- **Authentication JWT** complète (access + refresh tokens)
- **Gestion des rôles** avec permissions hiérarchiques
- **Permissions granulaires** au format `resource:action`
- **Multi-database** : PostgreSQL, MySQL, MongoDB
- **Cache Redis** avec fallback mémoire automatique
- **Auto-registration** des routes dans Swagger
- **100% asynchrone** (async/await)
- **Modèles extensibles** pour ajouter des champs personnalisés

## Installation

```bash
pip install fastapi-acl
```

### Dépendances optionnelles

```bash
# PostgreSQL
pip install fastapi-acl[postgresql]

# MySQL
pip install fastapi-acl[mysql]

# MongoDB
pip install fastapi-acl[mongodb]

# Redis (cache)
pip install fastapi-acl[redis]

# Toutes les dépendances
pip install fastapi-acl[all]
```

## Démarrage rapide

```python
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi_acl import ACLManager, ACLConfig, get_current_user, RequireRole

# Configuration
config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://user:pass@localhost/mydb",
    jwt_secret_key="your-super-secret-key-min-32-chars",
    enable_roles_feature=True,
    enable_permissions_feature=True,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await acl.initialize()
    yield
    await acl.close()

app = FastAPI(title="Mon API", lifespan=lifespan)
acl = ACLManager(config, app=app)

# Route protégée
@app.get("/protected")
async def protected(user=Depends(get_current_user)):
    return {"message": f"Bonjour {user.username}!"}

# Route admin uniquement
@app.get("/admin")
async def admin_only(user=Depends(RequireRole("admin"))):
    return {"message": "Bienvenue admin!"}
```

**C'est tout !** Les routes d'authentification sont automatiquement disponibles dans Swagger.

## Routes API générées

### Authentication (`/api/v1/auth`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/register` | Inscription |
| POST | `/login` | Connexion (retourne JWT) |
| POST | `/refresh` | Rafraîchir le token |
| GET | `/me` | Profil utilisateur |
| PUT | `/me` | Modifier son profil |
| POST | `/change-password` | Changer de mot de passe |

### Rôles (`/api/v1/roles`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste des rôles |
| POST | `/` | Créer un rôle |
| GET | `/{id}` | Détails d'un rôle |
| PATCH | `/{id}` | Modifier un rôle |
| DELETE | `/{id}` | Supprimer un rôle |
| POST | `/users/{user_id}/roles` | Assigner un rôle |
| DELETE | `/users/{user_id}/roles/{role_id}` | Retirer un rôle |

### Permissions (`/api/v1/permissions`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste des permissions |
| POST | `/` | Créer une permission |
| GET | `/search?q=` | Rechercher |
| GET | `/resources` | Lister les ressources |
| GET | `/categories` | Lister les catégories |

## Configuration

### Via variables d'environnement

Créez un fichier `.env` :

```env
# Database
ACL_DATABASE_TYPE=postgresql
ACL_POSTGRESQL_URI=postgresql+asyncpg://user:password@localhost:5432/mydb

# JWT
ACL_JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters
ACL_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ACL_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Features
ACL_ENABLE_AUTH_FEATURE=true
ACL_ENABLE_ROLES_FEATURE=true
ACL_ENABLE_PERMISSIONS_FEATURE=true

# Cache (optionnel)
ACL_ENABLE_CACHE=true
ACL_CACHE_BACKEND=redis
ACL_REDIS_URL=redis://localhost:6379/0

# Admin par défaut
ACL_CREATE_DEFAULT_ADMIN=true
ACL_DEFAULT_ADMIN_USERNAME=admin
ACL_DEFAULT_ADMIN_EMAIL=admin@example.com
ACL_DEFAULT_ADMIN_PASSWORD=admin123
```

### Via code Python

```python
from fastapi_acl import ACLConfig

config = ACLConfig(
    # Database
    database_type="postgresql",  # ou "mysql", "mongodb"
    postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",

    # JWT
    jwt_secret_key="your-super-secret-key-min-32-chars",
    jwt_algorithm="HS256",
    jwt_access_token_expire_minutes=30,
    jwt_refresh_token_expire_days=7,

    # Features
    enable_auth_feature=True,
    enable_roles_feature=True,
    enable_permissions_feature=True,

    # API
    enable_api_routes=True,
    api_prefix="/api/v1",

    # Cache
    enable_cache=True,
    cache_backend="redis",  # ou "memory"
    redis_url="redis://localhost:6379/0",

    # Développement
    create_default_admin=True,
    log_level="INFO",
)
```

## Dépendances FastAPI

### Protection par authentification

```python
from fastapi_acl import get_current_user, get_current_active_user, get_current_superuser

@app.get("/me")
async def my_profile(user=Depends(get_current_user)):
    return user

@app.get("/active-only")
async def active_users(user=Depends(get_current_active_user)):
    return {"user": user.username}

@app.get("/superuser-only")
async def superuser_only(user=Depends(get_current_superuser)):
    return {"message": "Vous êtes superuser!"}
```

### Protection par rôle

```python
from fastapi_acl import RequireRole, RequireRoles

# Un seul rôle requis
@app.get("/admin")
async def admin_panel(user=Depends(RequireRole("admin"))):
    return {"message": "Panel admin"}

# Un des rôles requis
@app.get("/staff")
async def staff_area(user=Depends(RequireRoles(["admin", "moderator"]))):
    return {"message": "Zone staff"}

# Tous les rôles requis
@app.get("/super-staff")
async def super_staff(user=Depends(RequireRoles(["admin", "moderator"], require_all=True))):
    return {"message": "Zone super staff"}
```

### Protection par permission

```python
from fastapi_acl import RequirePermission, RequirePermissions

# Une permission requise
@app.post("/posts")
async def create_post(user=Depends(RequirePermission("posts:create"))):
    return {"message": "Post créé"}

# Plusieurs permissions (toutes requises par défaut)
@app.put("/posts/{id}")
async def update_post(user=Depends(RequirePermissions(["posts:read", "posts:update"]))):
    return {"message": "Post modifié"}

# Au moins une permission
@app.get("/content")
async def view_content(user=Depends(RequirePermissions(["posts:read", "articles:read"], require_all=False))):
    return {"message": "Contenu accessible"}
```

## Permissions avec wildcards

Les permissions supportent les wildcards pour des droits globaux :

```python
# L'admin a la permission "*" (tout)
# Vérifie posts:create → True (wildcard match)

# Un modérateur a "posts:*"
# Vérifie posts:create → True
# Vérifie posts:delete → True
# Vérifie users:create → False
```

## Modèles personnalisés

### Utilisation de la Base SQLAlchemy

**Important** : Pour que les migrations Alembic fonctionnent correctement, vous **devez** utiliser la `Base` SQLAlchemy exportée par `fastapi-acl` pour tous vos modèles SQL.

#### Pourquoi ?

- **Cas 1 - Extension des modèles ACL** : Si vous étendez `SQLAuthUserModel`, il hérite déjà de notre `Base`. Vos modèles personnalisés doivent donc utiliser la même `Base` pour qu'Alembic détecte toutes les tables.

- **Cas 2 - Vos propres modèles** : Pour une gestion unifiée des migrations, utilisez notre `Base` pour que toutes les tables (ACL + application) soient gérées ensemble.

```python
from fastapi_acl import Base  # Utiliser cette Base pour tous vos modèles
from sqlalchemy import Column, String, Integer, ForeignKey

# Modèle propre à votre application
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))

# Modèle avec relation vers un utilisateur ACL
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey("acl_auth_users.id"))
    total = Column(Integer)
```

#### Base séparée (non recommandé)

Si vous utilisez votre propre `Base`, vous devrez configurer Alembic pour combiner les métadonnées :

```python
# alembic/env.py
from fastapi_acl import Base as ACLBase
from myapp.models import Base as AppBase
from sqlalchemy import MetaData

combined_metadata = MetaData()
for table in ACLBase.metadata.tables.values():
    table.tometadata(combined_metadata)
for table in AppBase.metadata.tables.values():
    table.tometadata(combined_metadata)

target_metadata = combined_metadata
```

### Ajouter des champs utilisateur (SQL)

```python
from sqlalchemy import Column, String, Integer
from fastapi_acl import SQLAuthUserModel, ACLManager, ACLConfig

class CustomUserModel(SQLAuthUserModel):
    __tablename__ = "users"  # Optionnel: changer le nom de table

    phone = Column(String(20), nullable=True)
    company_id = Column(Integer, nullable=True)
    department = Column(String(100), nullable=True)

config = ACLConfig(...)
acl = ACLManager(
    config,
    app=app,
    sql_user_model=CustomUserModel,
)
```

### Ajouter des champs utilisateur (MongoDB)

```python
from pydantic import Field
from fastapi_acl import MongoAuthUserModel, ACLManager, ACLConfig

class CustomUserModel(MongoAuthUserModel):
    phone: str | None = Field(None, max_length=20)
    company_id: str | None = None
    preferences: dict = Field(default_factory=dict)

config = ACLConfig(...)
acl = ACLManager(
    config,
    app=app,
    mongo_user_model=CustomUserModel,
    extra_user_indexes=["phone", "company_id"],  # Index MongoDB
)
```

## Migrations avec Alembic

### 1. Configuration `alembic/env.py`

```python
import asyncio
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Importer la Base et tous les modèles
from fastapi_acl import (
    Base,
    SQLAuthUserModel,
    SQLRoleModel,
    SQLUserRoleModel,
    SQLPermissionModel,
)

# Vos modèles personnalisés
from app.models import CustomUserModel

target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    # ... mode offline
else:
    run_migrations_online()
```

### 2. Commandes Alembic

```bash
# Générer une migration
alembic revision --autogenerate -m "Initial ACL tables"

# Appliquer les migrations
alembic upgrade head

# Voir l'état
alembic current
```

## Tables créées

| Table | Description |
|-------|-------------|
| `acl_auth_users` | Utilisateurs |
| `acl_roles` | Rôles |
| `acl_user_roles` | Association utilisateurs-rôles |
| `acl_permissions` | Permissions |

## Rôles et permissions par défaut

Au démarrage, le package crée automatiquement :

**Rôles :**
- `admin` : Tous les droits (`*`)
- `user` : Droits basiques (`profile:read`, `profile:update`)

**Permissions :**
- `profile:read`, `profile:update`
- `users:read`, `users:create`, `users:update`, `users:delete`
- `roles:read`, `roles:create`, `roles:update`, `roles:delete`, `roles:assign`
- `permissions:read`, `permissions:manage`

## Architecture

Le package suit une **Vertical Slice Architecture** avec Clean Architecture par feature :

```
fastapi_acl/
├── auth/                    # Feature Authentication
│   ├── domain/              # Entités et DTOs
│   ├── application/         # Use cases et interfaces
│   ├── infrastructure/      # Repositories et services
│   └── interface/           # Routes et dépendances
├── roles/                   # Feature Roles
├── permissions/             # Feature Permissions
├── shared/                  # Code partagé
│   ├── database/            # Connexions DB
│   ├── cache/               # Cache Redis/Memory
│   └── exceptions.py        # Exceptions
└── manager.py               # Point d'entrée
```

## Exemples complets

### Application minimale

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_acl import ACLManager, ACLConfig

config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
    jwt_secret_key="change-me-in-production-32-chars",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await acl.initialize()
    yield
    await acl.close()

app = FastAPI(lifespan=lifespan)
acl = ACLManager(config, app=app)
```

### Application complète avec toutes les features

```python
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi_acl import (
    ACLManager,
    ACLConfig,
    get_current_user,
    get_current_active_user,
    RequireRole,
    RequirePermission,
    RequirePermissions,
)

config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
    jwt_secret_key="your-production-secret-key-here",
    enable_roles_feature=True,
    enable_permissions_feature=True,
    enable_cache=True,
    redis_url="redis://localhost:6379/0",
    create_default_admin=True,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await acl.initialize()
    yield
    await acl.close()

app = FastAPI(title="Mon API Sécurisée", lifespan=lifespan)
acl = ACLManager(config, app=app)

@app.get("/")
async def home():
    return {"message": "Bienvenue!"}

@app.get("/profile")
async def my_profile(user=Depends(get_current_active_user)):
    return {"username": user.username, "email": user.email}

@app.get("/admin/dashboard")
async def admin_dashboard(user=Depends(RequireRole("admin"))):
    return {"message": "Dashboard admin", "user": user.username}

@app.post("/articles")
async def create_article(user=Depends(RequirePermission("articles:create"))):
    return {"message": "Article créé"}

@app.put("/articles/{id}")
async def update_article(
    id: int,
    user=Depends(RequirePermissions(["articles:read", "articles:update"]))
):
    return {"message": f"Article {id} modifié"}
```

## Licence

MIT License - voir [LICENSE](LICENSE)

## Contribuer

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## Support

- Issues : [GitHub Issues](https://github.com/your-repo/fastapi-acl/issues)
- Documentation : [Documentation complète](https://fastapi-acl.readthedocs.io)
