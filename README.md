# ALAK-ACL

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Package professionnel de gestion ACL (Access Control List) pour FastAPI.**

Gérez l'authentification, les rôles et les permissions dans vos applications FastAPI en quelques lignes de code.

## Caractéristiques

- **Authentication JWT** complète (access + refresh tokens)
- **Gestion des rôles** avec permissions hiérarchiques
- **Permissions granulaires** au format `resource:action`
- **Multi-tenant** : Isolation des données par tenant 
- **Multi-database** : PostgreSQL, MySQL, MongoDB
- **Cache Redis** avec fallback mémoire automatique
- **Auto-registration** des routes dans Swagger
- **100% asynchrone** (async/await)
- **Modèles extensibles** pour ajouter des champs personnalisés
- **Protection des données** : Empêche la suppression de rôles/permissions en cours d'utilisation

## Installation

```bash
pip install alak-acl
```

### Dépendances optionnelles

```bash
# PostgreSQL
pip install alak-acl[postgresql]

# MySQL
pip install alak-acl[mysql]

# MongoDB
pip install alak-acl[mongodb]

# Redis (cache)
pip install alak-acl[redis]

# Toutes les dépendances
pip install alak-acl[all]
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
    enable_public_registration=True,  # Pour apps classiques
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
| POST | `/register` | Inscription (désactivé par défaut) |
| POST | `/login` | Connexion (retourne JWT) |
| POST | `/refresh` | Rafraîchir le token |
| GET | `/me` | Profil utilisateur + rôles |
| PUT | `/me` | Modifier son profil |
| POST | `/forgot-password` | Envoie un email avec un lien de réinitialisation |
| POST | `/reset-password` | Réinitialisation du mot de passe |
| POST | `/change-password` | Changer de mot de passe |

> La route `/register` est désactivée par défaut pour le mode SaaS multi-tenant.
> Activez-la avec `enable_public_registration=True` pour les apps classiques.

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

## Modes d'utilisation

ALAK-ACL supporte trois modes d'utilisation selon vos besoins.

### Mode Classique

Pour les applications simples où les utilisateurs s'inscrivent eux-mêmes.

```python
config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://...",
    jwt_secret_key="your-secret-key",
    enable_roles_feature=True,
    enable_public_registration=True,
)
```

**Caractéristiques :**
- Route `/register` publique pour l'inscription
- Les utilisateurs créent leur compte via l'API
- Rôle par défaut assigné automatiquement
- Idéal pour : blogs, forums, apps grand public

### Mode SaaS Multi-Tenant

Pour les applications SaaS où des propriétaires de business (pressing, garage, etc.) créent leur compte puis gèrent leurs employés.

```python
config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://...",
    jwt_secret_key="your-secret-key",
    enable_roles_feature=True,
    enable_public_registration=False,  # L'app gère l'inscription
)
```

**Caractéristiques :**
- Route `/register` désactivée (l'app hôte gère l'inscription)
- L'app hôte crée les comptes propriétaires via `acl.create_account()` + crée le tenant
- Le propriétaire crée les comptes employés via son espace admin (`acl.create_account()`)
- Un utilisateur peut appartenir à plusieurs organisations
- Table de membership : user ↔ tenant ↔ role
- Idéal pour : SaaS B2B, plateformes multi-organisations

**Flux typique :**
1. Le propriétaire s'inscrit via un formulaire personnalisé de l'app hôte
2. L'app hôte crée le compte (`acl.create_account()`) + le tenant + assigne le rôle owner
3. Le propriétaire crée ses employés via son dashboard admin

### Mode B2B Privé

Pour les applications internes où seul l'administrateur crée les comptes.

```python
config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://...",
    jwt_secret_key="your-secret-key",
    enable_roles_feature=True,
    enable_public_registration=False,  # Désactivé
)
```

**Caractéristiques :**
- Route `/register` désactivée (retourne 403)
- L'administrateur crée tous les comptes via `acl.create_account()`
- Idéal pour : intranets, outils internes d'entreprise

## Architecture SaaS Multi-Tenant

ALAK-ACL est conçu pour les applications SaaS où un utilisateur peut appartenir à **plusieurs organisations (tenants)** avec des rôles différents dans chacune.

### Concepts clés

- **Utilisateurs globaux** : Les usernames et emails sont uniques globalement
- **Tenants gérés par l'app hôte** : Le package ne gère pas la création des tenants
- **Memberships** : Table pivot qui lie utilisateur ↔ tenant ↔ rôle
- **Propriétaires de tenant** : Créés par l'app hôte via un formulaire personnalisé
- **Employés** : Créés par le propriétaire via son espace admin

### Flux d'onboarding SaaS

**Étape 1 : Le propriétaire s'inscrit (via formulaire personnalisé de l'app)**
```python
# Route personnalisée de l'app hôte (ex: POST /signup)
@app.post("/signup")
async def signup_tenant_owner(data: SignupSchema):
    # 1. Créer le compte utilisateur via le package
    owner = await acl.create_account(
        username=data.username,
        email=data.email,
        password=data.password,
    )

    # 2. Créer le tenant dans votre base
    tenant = await my_app.create_tenant(
        name=data.business_name,  # Ex: "Pressing du Centre"
        owner_id=owner.id,
    )

    # 3. Assigner le rôle "owner" au propriétaire
    await acl.assign_role(
        user_id=owner.id,
        tenant_id=tenant.id,
        role_name="owner",
    )

    return {"user_id": owner.id, "tenant_id": tenant.id}
```

**Étape 2 : Le propriétaire crée ses employés (via son dashboard)**
```python
# Dans la route admin du propriétaire (ex: POST /admin/employees)
employee = await acl.create_account(
    username="marie_dupont",
    email="marie@pressing-du-centre.com",
    password="tempPassword123",
)

await acl.assign_role(
    user_id=employee.id,
    tenant_id=tenant.id,
    role_name="employee",
)
```

### Un utilisateur, plusieurs tenants

```python
# John est admin chez Acme Corp
await acl.assign_role(
    user_id=john.id,
    tenant_id="acme-corp-id",
    role_name="admin",
)

# John est aussi membre de Startup Inc
await acl.assign_role(
    user_id=john.id,
    tenant_id="startup-inc-id",
    role_name="user",
)

# Récupérer les tenants de John
tenants = await acl.get_user_tenants(john.id)
# ["acme-corp-id", "startup-inc-id"]
```

### Configuration

```python
config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://...",
    jwt_secret_key="your-secret-key",
    enable_roles_feature=True,
    # Désactivé par défaut pour SaaS
    enable_public_registration=False,
)
```

### Vérification d'appartenance à un tenant

```python
from fastapi import Depends, Header, HTTPException
from alak_acl import get_current_user, ACLManager

@app.get("/tenant/{tenant_id}/data")
async def get_tenant_data(
    tenant_id: str,
    user=Depends(get_current_user),
    acl: ACLManager = Depends(get_acl_manager),
):
    # Vérifier que l'utilisateur appartient au tenant
    user_tenants = await acl.get_user_tenants(user.id)
    if tenant_id not in user_tenants:
        raise HTTPException(403, "Vous n'appartenez pas à ce tenant")

    return await fetch_data_for_tenant(tenant_id)
```

### Middleware de tenant

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extraire le tenant_id du header
        tenant_id = request.headers.get("X-Tenant-ID")

        if not tenant_id:
            # Optionnel: extraire du subdomain
            # host = request.headers.get("host", "")
            # tenant_id = host.split(".")[0]
            pass

        request.state.tenant_id = tenant_id
        return await call_next(request)

app.add_middleware(TenantMiddleware)
```

### API /me avec tenant

L'endpoint `/me` accepte un header `X-Tenant-ID` pour retourner les rôles/permissions du tenant :

```python
# Sans X-Tenant-ID : retourne l'utilisateur + liste des tenants
GET /api/v1/auth/me
# Réponse
{
    "id": "user-uuid",
    "username": "john",
    "tenants": ["acme-corp-id", "startup-inc-id"],
    "roles": [],
    "permissions": []
}

# Avec X-Tenant-ID : retourne les rôles/permissions du tenant
GET /api/v1/auth/me
X-Tenant-ID: acme-corp-id
# Réponse
{
    "id": "user-uuid",
    "username": "john",
    "tenants": ["acme-corp-id", "startup-inc-id"],
    "roles": [{"name": "admin", "permissions": ["*"]}],
    "permissions": ["*"]
}
```

### Création de rôles par tenant

Les rôles peuvent être :
- **Globaux** (`tenant_id=None`) : Disponibles pour tous les tenants
- **Spécifiques** : Créés pour un tenant particulier

```python
# Via l'API - POST /api/v1/roles
{
    "name": "manager",
    "display_name": "Manager",
    "permissions": ["team:read", "team:update"],
    "tenant_id": "acme-corp-id"  # Rôle spécifique à ce tenant
}
```

## Protection contre la suppression

ALAK-ACL protège l'intégrité de vos données en empêchant la suppression d'entités en cours d'utilisation.

### Rôles

Un rôle **ne peut pas être supprimé** s'il :
- Est assigné à au moins un utilisateur
- Contient des permissions

```python
# Tentative de suppression d'un rôle utilisé
# DELETE /api/v1/roles/{role_id}

# Réponse 409 Conflict
{
    "detail": "Impossible de supprimer le rôle: il est assigné à 5 utilisateur(s)"
}

# Ou
{
    "detail": "Impossible de supprimer le rôle: il possède des permissions"
}
```

### Permissions

Une permission **ne peut pas être supprimée** si elle est assignée à au moins un rôle.

```python
# Tentative de suppression d'une permission utilisée
# DELETE /api/v1/permissions/{permission_id}

# Réponse 409 Conflict
{
    "detail": "Impossible de supprimer la permission: elle est utilisée par 3 rôle(s)"
}
```

### Workflow recommandé

1. **Pour supprimer un rôle** :
   - D'abord retirer le rôle de tous les utilisateurs
   - Puis vider les permissions du rôle (ou les conserver si ce sont des permissions réutilisables)
   - Enfin supprimer le rôle

2. **Pour supprimer une permission** :
   - D'abord retirer la permission de tous les rôles qui l'utilisent
   - Enfin supprimer la permission

## Modèles personnalisés

### Utilisation de la Base SQLAlchemy

**Important** : Pour que les migrations Alembic fonctionnent correctement, vous **devez** utiliser la `Base` SQLAlchemy exportée par `alak-acl` pour tous vos modèles SQL.

#### Pourquoi ?

- **Cas 1 - Extension des modèles ACL** : Si vous étendez `SQLAuthUserModel`, il hérite déjà de notre `Base`. Vos modèles personnalisés doivent donc utiliser la même `Base` pour qu'Alembic détecte toutes les tables.

- **Cas 2 - Vos propres modèles** : Pour une gestion unifiée des migrations, utilisez notre `Base` pour que toutes les tables (ACL + application) soient gérées ensemble.

```python
from alak_acl import Base  # Utiliser cette Base pour tous vos modèles
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
| `acl_auth_users` | Utilisateurs (globaux) |
| `acl_roles` | Rôles |
| `acl_memberships` | Pivot user ↔ tenant ↔ role |
| `acl_permissions` | Permissions |

### Structure des tables

#### `acl_auth_users`

Utilisateurs globaux (un utilisateur peut appartenir à plusieurs tenants).

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | VARCHAR(36) | UUID primary key |
| `username` | VARCHAR(50) | Nom d'utilisateur (unique globalement) |
| `email` | VARCHAR(255) | Email (unique globalement) |
| `hashed_password` | VARCHAR(255) | Mot de passe hashé |
| `is_active` | BOOLEAN | Compte actif |
| `is_verified` | BOOLEAN | Email vérifié |
| `is_superuser` | BOOLEAN | Super-administrateur |
| `created_at` | DATETIME | Date de création |
| `updated_at` | DATETIME | Date de mise à jour |
| `last_login` | DATETIME | Dernière connexion |

**Index uniques** :
- `username` - Unique globalement
- `email` - Unique globalement

#### `acl_roles`

Les rôles peuvent être globaux ou spécifiques à un tenant.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | VARCHAR(36) | UUID primary key |
| `name` | VARCHAR(50) | Nom du rôle |
| `display_name` | VARCHAR(100) | Nom d'affichage |
| `description` | VARCHAR(500) | Description |
| `permissions` | JSON | Liste des permissions |
| `is_active` | BOOLEAN | Rôle actif |
| `is_default` | BOOLEAN | Rôle par défaut pour les nouveaux membres |
| `is_system` | BOOLEAN | Rôle système (non supprimable) |
| `priority` | INTEGER | Priorité |
| `tenant_id` | VARCHAR(36) | NULL=global, sinon spécifique au tenant |
| `created_at` | DATETIME | Date de création |
| `updated_at` | DATETIME | Date de mise à jour |

**Index unique composite** :
- `(tenant_id, name)` - Un nom de rôle unique par tenant

#### `acl_memberships`

Table pivot pour lier utilisateurs, tenants et rôles.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | VARCHAR(36) | UUID primary key |
| `user_id` | VARCHAR(36) | FK vers acl_auth_users |
| `tenant_id` | VARCHAR(36) | ID du tenant (fourni par l'app hôte) |
| `role_id` | VARCHAR(36) | FK vers acl_roles |
| `assigned_at` | DATETIME | Date d'assignation |
| `assigned_by` | VARCHAR(36) | ID de l'utilisateur ayant assigné (optionnel) |

**Index unique** :
- `(user_id, tenant_id, role_id)` - Un utilisateur ne peut avoir le même rôle qu'une fois par tenant

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

### Application SaaS multi-tenant

```python
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from alak_acl import (
    ACLManager,
    ACLConfig,
    get_current_user,
    RequireRole,
)
from alak_acl.auth.domain.entities.auth_user import AuthUser

# Variable globale pour ACLManager
acl: ACLManager = None

# Middleware pour extraire le tenant_id
class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        request.state.tenant_id = tenant_id
        return await call_next(request)

config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
    jwt_secret_key="your-production-secret-key-here",
    enable_roles_feature=True,
    enable_public_registration=False,  # L'app gère l'inscription
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global acl
    acl = ACLManager(config, app=app)
    await acl.initialize()
    yield
    await acl.close()

app = FastAPI(title="API SaaS Multi-Tenant", lifespan=lifespan)
app.add_middleware(TenantMiddleware)

# Dépendance pour vérifier l'appartenance au tenant
async def verify_tenant_membership(
    user: AuthUser = Depends(get_current_user),
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Vérifie que l'utilisateur appartient au tenant spécifié."""
    user_tenants = await acl.get_user_tenants(user.id)
    if x_tenant_id not in user_tenants:
        raise HTTPException(
            status_code=403,
            detail="Vous n'appartenez pas à ce tenant"
        )
    return user, x_tenant_id

# Route personnalisée d'inscription pour les propriétaires de tenant
@app.post("/signup")
async def signup_tenant_owner(
    username: str,
    email: str,
    password: str,
    business_name: str,
):
    """Inscription d'un propriétaire de business (pressing, garage, etc.)."""
    # 1. Créer le compte utilisateur
    owner = await acl.create_account(
        username=username,
        email=email,
        password=password,
    )

    # 2. Créer le tenant dans votre base
    tenant = await my_app.create_tenant(name=business_name, owner_id=owner.id)

    # 3. Assigner le rôle "owner" au propriétaire
    await acl.assign_role(
        user_id=owner.id,
        tenant_id=tenant.id,
        role_name="owner",
    )

    return {"user_id": owner.id, "tenant_id": tenant.id, "business": business_name}

@app.get("/tenant/data")
async def get_tenant_data(membership=Depends(verify_tenant_membership)):
    user, tenant_id = membership
    return {
        "message": f"Données du tenant {tenant_id}",
        "user": user.username
    }

# Route pour que le propriétaire crée un employé
@app.post("/admin/employees")
async def create_employee(
    username: str,
    email: str,
    password: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    owner: AuthUser = Depends(get_current_user),  # Vérifier que c'est l'owner
):
    """Le propriétaire crée un compte employé."""
    # 1. Créer le compte employé
    employee = await acl.create_account(
        username=username,
        email=email,
        password=password,
    )

    # 2. L'ajouter au tenant avec le rôle "employee"
    await acl.assign_role(
        user_id=employee.id,
        tenant_id=x_tenant_id,
        role_name="employee",
    )

    return {"id": employee.id, "username": employee.username}
```

## Licence

MIT License - voir [LICENSE](LICENSE)

## Contribuer

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## Support

- Issues : [GitHub Issues](https://github.com/your-repo/fastapi-acl/issues)
- Documentation : [Documentation complète](https://fastapi-acl.readthedocs.io)









