# PROMPT : Création d'un package FastAPI ACL avec Architecture Modulaire par Features

## CONTEXTE
Je veux créer un package Python professionnel nommé "fastapi-acl" pour gérer l'authentification et les permissions (ACL - Access Control List) dans des applications FastAPI.

## ORGANISATION ARCHITECTURALE

### Principe : Vertical Slice Architecture (organisation par features)
- Chaque feature est un module autonome et complet
- Chaque feature contient ses propres couches : domain, application, infrastructure, interface
- Le code partagé est isolé dans un dossier "shared"
- Clean Architecture au sein de chaque feature

### Structure exacte du projet
```
fastapi-acl/
├── auth/                                # FEATURE: Authentication
│   ├── application/
│   │   ├── interface/                   # Interfaces (ports/abstractions)
│   │   └── usecases/                    # Use cases métier
│   ├── domain/
│   │   ├── dtos/                        # Data Transfer Objects
│   │   └── entities/                    # Entités métier
│   ├── infrastructure/
│   │   ├── mappers/                     # Mappers Entity ↔ Model
│   │   ├── models/                      # Modèles DB
│   │   └── repositories/                # Implémentations repositories
│   └── interface/
│       ├── admin/                       # Routes admin
│       ├── api.py                       # Routes publiques
│       ├── dependencies.py              # Dépendances FastAPI
│       └── schemas.py                   # Schémas Pydantic API
│
├── permissions/                         # FEATURE: Permissions (à créer)
├── roles/                               # FEATURE: Roles (à créer)
├── users/                               # FEATURE: Users (à créer)
│
├── shared/                              # Code partagé
│   ├── config.py                        # Configuration Pydantic
│   ├── database/                        # Connexions DB
│   │   ├── mongodb.py
│   │   ├── postgresql.py
│   │   ├── mysql.py
│   │   └── factory.py
│   ├── cache/                           # Cache Redis/Memory
│   │   ├── base.py
│   │   ├── redis_cache.py
│   │   ├── memory_cache.py
│   │   └── factory.py
│   ├── exceptions.py
│   └── logging.py
│
├── manager.py                           # ACLManager principal
├── __init__.py                          # Point d'entrée
├── tests/                               # Tests par feature
├── examples/
├── docs/
└── setup.py
```

## FEATURE 1 : AUTH (Authentification)

### Responsabilité
Gérer l'authentification des utilisateurs : inscription, connexion, gestion des tokens JWT, sessions.

### Couche Domain (auth/domain/)

**Entities (entités métier pures):**
- AuthUser : id, username, email, hashed_password, is_active, is_verified, created_at, updated_at
  - Méthodes : verify_password(), is_authenticated()

**DTOs (objets de transfert):**
- LoginDTO : username, password
- RegisterDTO : username, email, password
- TokenDTO : access_token, refresh_token, token_type, expires_in

### Couche Application (auth/application/)

**Interfaces (abstractions):**
- IAuthRepository : interface pour le repository d'authentification
  - Méthodes : create_user(), get_by_username(), get_by_email(), get_by_id(), update_user()
- ITokenService : interface pour la gestion des tokens
  - Méthodes : create_access_token(), decode_token(), create_refresh_token()
- IPasswordHasher : interface pour le hashage de mots de passe
  - Méthodes : hash(), verify()

**Use Cases (logique métier):**
- LoginUseCase : gérer la connexion d'un utilisateur
  - Input : LoginDTO
  - Output : TokenDTO
  - Logique : vérifier credentials, générer tokens
- RegisterUseCase : gérer l'inscription d'un utilisateur
  - Input : RegisterDTO
  - Output : AuthUser
  - Logique : vérifier unicité, hasher password, créer user
- RefreshTokenUseCase : rafraîchir un token
  - Input : refresh_token string
  - Output : TokenDTO
  - Logique : valider refresh token, générer nouveau access token

### Couche Infrastructure (auth/infrastructure/)

**Models (modèles DB):**
- MongoAuthUserModel : modèle Pydantic pour MongoDB
- SQLAuthUserModel : modèle SQLAlchemy pour PostgreSQL/MySQL

**Mappers (conversion Entity ↔ Model):**
- AuthUserMapper : 
  - to_entity(model) → AuthUser
  - to_model(entity, db_type) → Model

**Repositories (implémentations):**
- MongoDBAuthRepository : implémentation IAuthRepository pour MongoDB
- PostgreSQLAuthRepository : implémentation IAuthRepository pour PostgreSQL
- MySQLAuthRepository : implémentation IAuthRepository pour MySQL

**Services:**
- JWTTokenService : implémentation ITokenService avec python-jose
- BcryptPasswordHasher : implémentation IPasswordHasher avec bcrypt

### Couche Interface (auth/interface/)

**Schemas (Pydantic pour API):**
- LoginRequest, LoginResponse
- RegisterRequest, UserResponse
- RefreshTokenRequest, RefreshTokenResponse

**Dependencies (dépendances FastAPI):**
- get_auth_repository() : récupérer le repository
- get_token_service() : récupérer le service de tokens
- get_login_usecase() : instancier LoginUseCase
- get_register_usecase() : instancier RegisterUseCase
- get_current_user() : dépendance pour récupérer l'utilisateur authentifié

**Routes publiques (api.py):**
- POST /auth/register : inscription
- POST /auth/login : connexion
- POST /auth/refresh : rafraîchir token
- GET /auth/me : informations utilisateur connecté
- POST /auth/logout : déconnexion

**Routes admin (admin/):**
- GET /admin/auth/users : lister utilisateurs
- PUT /admin/auth/users/{id}/activate : activer un utilisateur
- PUT /admin/auth/users/{id}/deactivate : désactiver
- DELETE /admin/auth/users/{id} : supprimer

## SHARED (Code partagé entre features)

### Configuration (shared/config.py)
**ACLConfig (Pydantic Settings):**
- Database : database_type, mongodb_uri, postgresql_uri, mysql_uri
- Redis : enable_cache, redis_url, cache_ttl, cache_backend
- JWT : jwt_secret_key, jwt_algorithm, jwt_access_token_expire_minutes
- API : enable_api_routes, api_prefix
- Features : enable_auth_feature, enable_permissions_feature, enable_roles_feature
- Dev : disable_auth_for_dev, create_default_admin, log_level

### Database (shared/database/)
- Connexions pour MongoDB (motor), PostgreSQL (asyncpg + SQLAlchemy), MySQL (aiomysql + SQLAlchemy)
- DatabaseFactory : créer la connexion selon le type de DB

### Cache (shared/cache/)
- CacheBackend : interface abstraite
- RedisCache : implémentation Redis avec redis.asyncio
- MemoryCache : implémentation en mémoire (fallback)
- CacheFactory : créer le cache selon la config

### Exceptions (shared/exceptions.py)
- ACLException (base)
- AuthenticationError, InvalidCredentialsError, InvalidTokenError
- UserNotActiveError, UserAlreadyExistsError
- PermissionDeniedError, RoleNotFoundError

## MANAGER PRINCIPAL (manager.py)

### ACLManager
**Responsabilités:**
- Point d'entrée unique du package
- Initialiser toutes les connexions (DB, cache)
- Initialiser toutes les features activées
- Auto-enregistrer les routes dans FastAPI si une app est fournie
- Fournir des getters pour accéder aux repositories et services

**Méthodes:**
- `__init__(config, app=None)` : constructeur, auto-register routes si app fournie
- `async initialize()` : initialiser DB, cache, features
- `async close()` : fermer toutes les connexions
- `get_auth_repository()` : retourner le repository d'auth
- `get_token_service()` : retourner le service de tokens

## FONCTIONNALITÉS TECHNIQUES

### Multi-Database (async)
- MongoDB avec motor
- PostgreSQL avec asyncpg + SQLAlchemy 2.0 async
- MySQL avec aiomysql + SQLAlchemy 2.0 async
- Pattern Repository pour abstraire la DB
- Pattern Mapper pour convertir Entity ↔ Model

### Cache Redis (async)
- Cache des permissions utilisateur
- Rate limiting
- Fallback automatique vers cache mémoire si Redis indisponible
- TTL configurable

### JWT Authentication
- Access token (courte durée)
- Refresh token (longue durée)
- Signature avec python-jose
- Extraction et validation dans les dépendances FastAPI

### Auto-registration des routes
- Quand le dev passe l'app FastAPI à ACLManager, toutes les routes sont automatiquement enregistrées
- Routes visibles dans Swagger sans configuration supplémentaire
- Préfixe d'API configurable

### Rate Limiting (optionnel)
- Service de rate limiting avec Redis
- Middleware FastAPI
- Headers X-RateLimit-* dans les réponses

## UTILISATION ATTENDUE PAR LE DÉVELOPPEUR

Le développeur doit pouvoir utiliser le package en 3 lignes :
```python
from fastapi import FastAPI
from fastapi_acl import ACLManager, ACLConfig

app = FastAPI()

config = ACLConfig(
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://user:pass@localhost/db",
    enable_cache=True,
    redis_url="redis://localhost:6379/0",
    enable_auth_feature=True,
    enable_api_routes=True
)

# ✅ Passer l'app pour auto-register les routes
acl = ACLManager(config, app=app)

@app.on_event("startup")
async def startup():
    await acl.initialize()

@app.on_event("shutdown")
async def shutdown():
    await acl.close()

# Les routes sont automatiquement dans Swagger !
# GET /api/v1/auth/me
# POST /api/v1/auth/login
# etc.
```

## CONTRAINTES TECHNIQUES

### Stack obligatoire
- Python 3.10+
- FastAPI >= 0.104.0
- Pydantic v2 >= 2.0.0
- SQLAlchemy 2.0 async
- motor (MongoDB async)
- redis.asyncio
- python-jose (JWT)
- passlib + bcrypt (password hashing)

### Principes
- 100% asynchrone (async/await partout)
- Type hints obligatoires
- Docstrings Google Style en français
- Clean Architecture stricte
- SOLID principles
- Dependency Injection
- Tests avec pytest-asyncio

### Organisation
- Code (variables, fonctions, classes) en anglais
- Commentaires et docstrings en français
- Documentation utilisateur en français
- Chaque feature est autonome et testable indépendamment
- Le code partagé (shared) ne dépend d'aucune feature
- Les features peuvent dépendre du code partagé mais pas entre elles

## LIVRABLES ATTENDUS

1. **Package complet** avec la structure exacte décrite
2. **Feature AUTH complète** et fonctionnelle
3. **Tests unitaires** pour la feature AUTH (coverage 80%+)
4. **Exemples d'utilisation** (examples/)
5. **Documentation** (README.md + docs/)
6. **setup.py et pyproject.toml** pour distribution PyPI
7. **.env.example** avec toutes les variables
8. **CI/CD** (GitHub Actions) pour tests et linting

## FEATURES FUTURES (structure identique à AUTH)

- **permissions/** : gérer les permissions (resource:action)
- **roles/** : gérer les rôles et associations role-permissions
- **users/** : gérer les utilisateurs et leurs rôles

Chaque feature suivra exactement la même structure que AUTH :
- domain/ (entities, dtos)
- application/ (interface, usecases)
- infrastructure/ (mappers, models, repositories)
- interface/ (admin, api.py, dependencies.py, schemas.py)

## NOTES IMPORTANTES

- Le développeur ne doit JAMAIS avoir à écrire de code pour enregistrer les routes
- Tout doit être configurable via ACLConfig
- Le package doit fonctionner avec MongoDB OU PostgreSQL OU MySQL (pas les 3 en même temps)
- Le cache Redis est optionnel avec fallback automatique vers mémoire
- Les migrations Alembic doivent être gérées automatiquement (à détailler plus tard)
- La sécurité est primordiale : hashage bcrypt, tokens JWT signés, validation stricte

Génère ce package complet en respectant scrupuleusement cette architecture modulaire par features.