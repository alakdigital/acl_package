# Guide de démarrage rapide

## Installation

```bash
pip install fastapi-acl
```

Ou pour le développement:

```bash
git clone https://github.com/example/fastapi-acl.git
cd fastapi-acl
pip install -e ".[dev]"
```

## Configuration minimale

1. Créez un fichier `.env` (ou copiez `.env.example`):

```env
ACL_DATABASE_TYPE=postgresql
ACL_POSTGRESQL_URI=postgresql+asyncpg://postgres:password@localhost:5432/mydb
ACL_JWT_SECRET_KEY=votre-cle-secrete-minimum-32-caracteres
```

2. Créez votre application FastAPI:

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_acl import ACLManager, ACLConfig

config = ACLConfig()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await acl.initialize()
    yield
    await acl.close()

app = FastAPI(lifespan=lifespan)
acl = ACLManager(config, app=app)
```

3. Lancez l'application:

```bash
uvicorn main:app --reload
```

4. Accédez à Swagger UI: http://localhost:8000/docs

## Routes automatiques

Les routes suivantes sont automatiquement enregistrées:

### Routes publiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/auth/register` | Inscription |
| POST | `/api/v1/auth/login` | Connexion |
| POST | `/api/v1/auth/refresh` | Rafraîchir le token |
| GET | `/api/v1/auth/me` | Info utilisateur connecté |
| POST | `/api/v1/auth/logout` | Déconnexion |

### Routes admin

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/admin/auth/users` | Lister les utilisateurs |
| GET | `/api/v1/admin/auth/users/{id}` | Détails d'un utilisateur |
| PUT | `/api/v1/admin/auth/users/{id}/activate` | Activer un compte |
| PUT | `/api/v1/admin/auth/users/{id}/deactivate` | Désactiver un compte |
| DELETE | `/api/v1/admin/auth/users/{id}` | Supprimer un utilisateur |

## Protéger vos routes

```python
from fastapi import Depends
from fastapi_acl import get_current_active_user, AuthUser

@app.get("/protected")
async def protected_route(user: AuthUser = Depends(get_current_active_user)):
    return {"message": f"Bonjour {user.username}!"}
```

## Workflow d'authentification

1. **Inscription**: POST `/api/v1/auth/register`
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "monmotdepasse123"
}
```

2. **Connexion**: POST `/api/v1/auth/login`
```json
{
  "username": "john",
  "password": "monmotdepasse123"
}
```

Réponse:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

3. **Utiliser le token**:
```bash
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/api/v1/auth/me
```

4. **Rafraîchir le token**: POST `/api/v1/auth/refresh`
```json
{
  "refresh_token": "eyJ..."
}
```

## Configuration complète

Voir le fichier `.env.example` pour toutes les options de configuration.
