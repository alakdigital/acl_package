"""
Exemple d'utilisation avec des champs personnalisés.

Cet exemple montre comment ajouter des colonnes/champs personnalisés
au modèle utilisateur pour PostgreSQL/MySQL et MongoDB.

Note:
- Pour SQL (PostgreSQL/MySQL): L'ID est un UUID stocké en CHAR(36)
- Pour MongoDB: L'_id est généré automatiquement par MongoDB (ObjectId)
"""

from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# ============================================
# OPTION 1: Champs personnalisés avec PostgreSQL/MySQL
# ============================================

from sqlalchemy import Column, String, Integer, Boolean as SQLBoolean

from fastapi_acl import (
    ACLManager,
    ACLConfig,
    AuthUser,
    get_current_user,
    get_current_active_user,
    # Modèles extensibles
    SQLAuthUserModel,
    create_user_model,
)


# Méthode 1A: Créer une sous-classe du modèle SQL
class CustomUserModel(SQLAuthUserModel):
    """
    Modèle utilisateur personnalisé avec des colonnes supplémentaires.

    Ces colonnes seront créées automatiquement dans la table.
    """
    __tablename__ = "users"  # Nom personnalisé de la table

    # Colonnes personnalisées
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    department = Column(String(50), nullable=True)
    employee_id = Column(String(20), nullable=True, unique=True)
    age = Column(Integer, nullable=True)
    is_premium = Column(SQLBoolean, default=False)


# Méthode 1B: Alternative avec la factory function (création dynamique)
# CustomUserModel = create_user_model(
#     tablename="users",
#     extra_columns={
#         "phone": Column(String(20), nullable=True),
#         "company": Column(String(100), nullable=True),
#         "department": Column(String(50), nullable=True),
#         "employee_id": Column(String(20), nullable=True, unique=True),
#         "age": Column(Integer, nullable=True),
#         "is_premium": Column(SQLBoolean, default=False),
#     }
# )


# ============================================
# OPTION 2: Champs personnalisés avec MongoDB
# ============================================

from fastapi_acl import MongoAuthUserModel, create_mongo_user_model


# Méthode 2A: Créer une sous-classe du modèle MongoDB
class CustomMongoUserModel(MongoAuthUserModel):
    """
    Modèle utilisateur MongoDB avec des champs supplémentaires.

    Note: L'_id est généré automatiquement par MongoDB (ObjectId).
    """
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=50)
    employee_id: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=150)
    is_premium: bool = False
    tags: list = Field(default_factory=list)


# Méthode 2B: Alternative avec la factory function
# CustomMongoUserModel = create_mongo_user_model(
#     extra_fields={
#         "phone": (Optional[str], Field(None, max_length=20)),
#         "company": (Optional[str], Field(None, max_length=100)),
#         "department": (Optional[str], Field(None, max_length=50)),
#         "employee_id": (Optional[str], Field(None, max_length=20)),
#         "age": (Optional[int], Field(None, ge=0, le=150)),
#         "is_premium": (bool, False),
#     }
# )


# ============================================
# Configuration avec le modèle personnalisé
# ============================================

config = ACLConfig(
    # PostgreSQL avec modèle personnalisé
    database_type="postgresql",
    postgresql_uri="postgresql+asyncpg://postgres:password@localhost:5432/acl_db",
    users_table_name="users",  # Doit correspondre à __tablename__

    # Cache Redis
    enable_cache=True,
    redis_url="redis://localhost:6379/0",

    # JWT
    jwt_secret_key="votre-cle-secrete-de-minimum-32-caracteres-ici",
    jwt_access_token_expire_minutes=30,

    # API
    enable_api_routes=True,
    api_prefix="/api/v1",

    # Features
    enable_auth_feature=True,

    # Développement
    create_default_admin=True,
    log_level="DEBUG",
)


# Configuration MongoDB alternative
# config_mongo = ACLConfig(
#     database_type="mongodb",
#     mongodb_uri="mongodb://localhost:27017",
#     mongodb_database="acl_db",
#     users_table_name="users",
#     extra_user_indexes="phone,company,employee_id",  # Index sur champs personnalisés
#     # ... autres configs
# )


# ============================================
# Application FastAPI
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    await acl.initialize()
    yield
    await acl.close()


app = FastAPI(
    title="Application avec champs personnalisés",
    description="Exemple d'utilisation des champs personnalisés fastapi-acl",
    version="1.0.0",
    lifespan=lifespan,
)


# Initialisation avec le modèle personnalisé
acl = ACLManager(
    config=config,
    app=app,
    sql_user_model=CustomUserModel,  # Passer le modèle personnalisé
    # mongo_user_model=CustomMongoUserModel,  # Pour MongoDB
    # extra_user_indexes=["phone", "company", "employee_id"],  # Index MongoDB
)


# ============================================
# Schémas Pydantic pour les API
# ============================================

class UserProfileUpdate(BaseModel):
    """Schéma pour mettre à jour le profil utilisateur."""
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=150)


class UserProfileResponse(BaseModel):
    """Réponse avec les informations du profil."""
    id: str
    username: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    employee_id: Optional[str] = None
    age: Optional[int] = None
    is_premium: bool = False


# ============================================
# Routes personnalisées utilisant les champs custom
# ============================================

@app.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: AuthUser = Depends(get_current_active_user)):
    """
    Récupère le profil complet de l'utilisateur connecté.

    Inclut tous les champs personnalisés.
    """
    return UserProfileResponse(
        id=current_user.id,  # ID est déjà un string
        username=current_user.username,
        email=current_user.email,
        phone=current_user.get_extra("phone"),
        company=current_user.get_extra("company"),
        department=current_user.get_extra("department"),
        employee_id=current_user.get_extra("employee_id"),
        age=current_user.get_extra("age"),
        is_premium=current_user.get_extra("is_premium", False),
    )


@app.patch("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile: UserProfileUpdate,
    current_user: AuthUser = Depends(get_current_active_user),
):
    """
    Met à jour le profil de l'utilisateur connecté.

    Seuls les champs fournis sont mis à jour.
    """
    # Récupérer le repository
    repo = acl.get_auth_repository()

    # Mettre à jour les champs personnalisés
    if profile.phone is not None:
        current_user.set_extra("phone", profile.phone)
    if profile.company is not None:
        current_user.set_extra("company", profile.company)
    if profile.department is not None:
        current_user.set_extra("department", profile.department)
    if profile.age is not None:
        current_user.set_extra("age", profile.age)

    # Sauvegarder
    updated_user = await repo.update_user(current_user)

    return UserProfileResponse(
        id=updated_user.id,  # ID est déjà un string
        username=updated_user.username,
        email=updated_user.email,
        phone=updated_user.get_extra("phone"),
        company=updated_user.get_extra("company"),
        department=updated_user.get_extra("department"),
        employee_id=updated_user.get_extra("employee_id"),
        age=updated_user.get_extra("age"),
        is_premium=updated_user.get_extra("is_premium", False),
    )


@app.get("/users/by-company/{company}")
async def get_users_by_company(
    company: str,
    current_user: AuthUser = Depends(get_current_active_user),
):
    """
    Recherche les utilisateurs par entreprise.

    Utilise la méthode de recherche par champ personnalisé.
    """
    repo = acl.get_auth_repository()

    # Recherche par champ personnalisé (disponible sur les deux repos)
    users = await repo.list_by_extra_field(
        field_name="company",
        value=company,
        limit=50,
    )

    return [
        {
            "id": user.id,  # ID est déjà un string
            "username": user.username,
            "company": user.get_extra("company"),
            "department": user.get_extra("department"),
        }
        for user in users
    ]


@app.get("/users/by-employee-id/{employee_id}")
async def get_user_by_employee_id(
    employee_id: str,
    current_user: AuthUser = Depends(get_current_active_user),
):
    """
    Recherche un utilisateur par son ID employé.
    """
    repo = acl.get_auth_repository()

    user = await repo.find_by_extra_field(
        field_name="employee_id",
        value=employee_id,
    )

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return {
        "id": user.id,  # ID est déjà un string
        "username": user.username,
        "email": user.email,
        "employee_id": user.get_extra("employee_id"),
        "company": user.get_extra("company"),
    }


# ============================================
# Point d'entrée
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
