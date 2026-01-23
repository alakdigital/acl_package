# Architecture du package fastapi-acl

## Vue d'ensemble

fastapi-acl utilise une **Vertical Slice Architecture** (organisation par features) combinée avec les principes de **Clean Architecture** au sein de chaque feature.

## Structure du projet

```
fastapi_acl/
├── auth/                          # Feature: Authentication
│   ├── domain/                    # Couche Domaine
│   │   ├── entities/              # Entités métier pures
│   │   └── dtos/                  # Data Transfer Objects
│   ├── application/               # Couche Application
│   │   ├── interface/             # Interfaces (ports/abstractions)
│   │   └── usecases/              # Cas d'utilisation métier
│   ├── infrastructure/            # Couche Infrastructure
│   │   ├── models/                # Modèles de base de données
│   │   ├── mappers/               # Mappers Entity ↔ Model
│   │   ├── repositories/          # Implémentations des repositories
│   │   └── services/              # Services techniques (JWT, bcrypt)
│   └── interface/                 # Couche Interface
│       ├── admin/                 # Routes d'administration
│       ├── api.py                 # Routes publiques
│       ├── dependencies.py        # Dépendances FastAPI
│       └── schemas.py             # Schémas Pydantic pour l'API
│
├── shared/                        # Code partagé entre features
│   ├── config.py                  # Configuration Pydantic
│   ├── exceptions.py              # Exceptions personnalisées
│   ├── logging.py                 # Configuration du logging
│   ├── database/                  # Connexions DB (MongoDB, PostgreSQL, MySQL)
│   └── cache/                     # Cache (Redis, Memory)
│
├── manager.py                     # Point d'entrée principal (ACLManager)
└── __init__.py                    # Exports publics
```

## Principes architecturaux

### 1. Séparation des responsabilités

Chaque couche a une responsabilité unique:

- **Domain**: Logique métier pure, indépendante de l'infrastructure
- **Application**: Orchestration des cas d'utilisation
- **Infrastructure**: Implémentations techniques (DB, cache, services)
- **Interface**: Exposition via l'API HTTP

### 2. Inversion des dépendances

Les couches hautes (Domain, Application) ne dépendent pas des couches basses (Infrastructure). Ceci est réalisé via des interfaces:

```
Application définit IAuthRepository (interface)
       ↓
Infrastructure implémente PostgreSQLAuthRepository
```

### 3. Pattern Repository

Le repository abstrait l'accès aux données:

```python
# Interface (application/interface/auth_repository.py)
class IAuthRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[AuthUser]:
        pass

# Implémentation (infrastructure/repositories/postgresql_repository.py)
class PostgreSQLAuthRepository(IAuthRepository):
    async def get_by_id(self, user_id: UUID) -> Optional[AuthUser]:
        # Implémentation spécifique PostgreSQL
```

### 4. Pattern Mapper

Les mappers convertissent entre les entités domaine et les modèles DB:

```python
# Entité domaine (pure, pas de dépendance DB)
@dataclass
class AuthUser:
    id: UUID
    username: str
    email: str

# Modèle DB (spécifique SQLAlchemy)
class SQLAuthUserModel(Base):
    __tablename__ = "acl_auth_users"
    id = Column(UUID, primary_key=True)

# Mapper
class AuthUserMapper:
    @staticmethod
    def to_entity(model: SQLAuthUserModel) -> AuthUser:
        return AuthUser(id=model.id, ...)

    @staticmethod
    def to_sql_model(entity: AuthUser) -> SQLAuthUserModel:
        return SQLAuthUserModel(id=entity.id, ...)
```

### 5. Use Cases

Les use cases encapsulent la logique métier:

```python
class LoginUseCase:
    def __init__(
        self,
        auth_repository: IAuthRepository,
        token_service: ITokenService,
        password_hasher: IPasswordHasher,
    ):
        self._auth_repository = auth_repository
        self._token_service = token_service
        self._password_hasher = password_hasher

    async def execute(self, login_dto: LoginDTO) -> TokenDTO:
        # 1. Récupérer l'utilisateur
        user = await self._auth_repository.get_by_username(login_dto.username)

        # 2. Vérifier le mot de passe
        if not self._password_hasher.verify(login_dto.password, user.hashed_password):
            raise InvalidCredentialsError()

        # 3. Générer les tokens
        return TokenDTO(
            access_token=self._token_service.create_access_token(user.id, user.username),
            refresh_token=self._token_service.create_refresh_token(user.id, user.username),
        )
```

## Flux de données

```
HTTP Request
    ↓
[Interface Layer] - api.py reçoit la requête
    ↓
[Pydantic Schema] - Validation des données (LoginRequest)
    ↓
[DTO] - Conversion en DTO métier (LoginDTO)
    ↓
[Use Case] - Exécution de la logique métier
    ↓
[Repository Interface] - Appel abstrait au repository
    ↓
[Repository Implementation] - Accès réel à la DB
    ↓
[Mapper] - Conversion Model → Entity
    ↓
[Entity] - Traitement métier
    ↓
[DTO] - Résultat (TokenDTO)
    ↓
[Pydantic Schema] - Sérialisation (LoginResponse)
    ↓
HTTP Response
```

## Multi-base de données

Le package supporte plusieurs bases de données via le pattern Factory:

```python
class DatabaseFactory:
    @staticmethod
    def create(config: ACLConfig) -> BaseDatabase:
        if config.database_type == "mongodb":
            return MongoDBDatabase(config.mongodb_uri)
        elif config.database_type == "postgresql":
            return PostgreSQLDatabase(config.postgresql_uri)
        elif config.database_type == "mysql":
            return MySQLDatabase(config.mysql_uri)
```

## Extension: Ajouter une nouvelle feature

Pour ajouter une feature (ex: `permissions/`):

1. Créer la structure de dossiers identique à `auth/`
2. Définir les entités dans `domain/entities/`
3. Définir les interfaces dans `application/interface/`
4. Implémenter les use cases dans `application/usecases/`
5. Implémenter les repositories pour chaque DB
6. Créer les routes dans `interface/`
7. Enregistrer les routes dans `ACLManager`
