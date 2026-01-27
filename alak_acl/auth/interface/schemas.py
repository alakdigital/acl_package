"""
Schémas Pydantic pour l'API d'authentification.
"""

from datetime import datetime
import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================
# Request Schemas
# ============================================


class LoginRequest(BaseModel):
    """Schéma de requête pour la connexion."""

    username: str = Field(..., description="Nom d'utilisateur")
    password: str
    
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Veuillez saisir le username")
        return v

    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Veuillez saisir le mot de passe")
        return v
    
    model_config = {
        "json_schema_extra": {
           "example": {
                'username': "alakacl",
                'password': "mypassword"
           }
        }
    }



class RegisterRequest(BaseModel):
    """Schéma de requête pour l'inscription."""

    username: str
    email: EmailStr
    password: str
    tenant_id: Optional[str] = Field(None, description="Identifiant du tenant (optionnel)")

    
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le nom d'utilisateur ne peut pas être vide")
        v = v.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores"
            )
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Le nom d'utilisateur doit contenir entre 3 et 30 caractères")
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le mot de passe ne peut pas être vide")
        v = v.strip()
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        # if not re.search(r"[A-Z]", v):
        #     raise ValueError("Le mot de passe doit contenir au moins une lettre majuscule")
        # if not re.search(r"[a-z]", v):
        #     raise ValueError("Le mot de passe doit contenir au moins une lettre minuscule")
        # if not re.search(r"[0-9]", v):
        #     raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
        #     raise ValueError("Le mot de passe doit contenir au moins un symbole spécial")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        Non vide et format email valide (EmailStr s'en occupe)
        """
        if not v or not v.strip():
            raise ValueError("L'email ne peut pas être vide")
        v = v.strip()
        return v
    
    
    model_config = {
        "json_schema_extra": {
           "example": {
                'username': "alakacl",
                'email': "alakacl@gmail.com",
                'password': "mypassword"
           }
        }
    }

class RefreshTokenRequest(BaseModel):
    """Schéma de requête pour rafraîchir un token."""

    refresh_token: str

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("L'email ne peut pas être vide")
        v = v.strip()
        return v

# ============================================
# Response Schemas
# ============================================


class RoleResponse(BaseModel):
    """Schéma de réponse pour un rôle."""

    id: str = Field(..., description="Identifiant unique du rôle")
    name: str = Field(..., description="Nom du rôle")
    display_name: Optional[str] = Field(None, description="Nom d'affichage")
    permissions: list[str] = Field(default_factory=list, description="Liste des permissions")
    tenant_id: Optional[str] = Field(None, description="Identifiant du tenant")

    class Config:
        """Configuration Pydantic."""
        from_attributes = True


class LoginResponse(BaseModel):
    """Schéma de réponse pour la connexion."""

    access_token: str = Field(..., description="Token d'accès JWT")
    refresh_token: str = Field(..., description="Token de rafraîchissement")
    token_type: str = Field(default="Bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée de validité en secondes")


class RefreshTokenResponse(BaseModel):
    """Schéma de réponse pour le rafraîchissement de token."""

    access_token: str = Field(..., description="Nouveau token d'accès JWT")
    token_type: str = Field(default="Bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée de validité en secondes")


class UserResponse(BaseModel):
    """Schéma de réponse pour les informations utilisateur."""

    id: str = Field(..., description="Identifiant unique (UUID)")
    username: str = Field(..., description="Nom d'utilisateur")
    email: EmailStr = Field(..., description="Adresse email")
    is_active: bool = Field(..., description="Compte actif")
    is_verified: bool = Field(..., description="Email vérifié")
    is_superuser: bool = Field(..., description="Administrateur")
    tenant_id: Optional[str] = Field(None, description="Identifiant du tenant")
    created_at: datetime = Field(..., description="Date de création")
    last_login: Optional[datetime] = Field(None, description="Dernière connexion")

    class Config:
        """Configuration Pydantic."""
        from_attributes = True


class UserMeResponse(BaseModel):
    """Schéma de réponse pour /me avec rôles et permissions."""

    id: str = Field(..., description="Identifiant unique (UUID)")
    username: str = Field(..., description="Nom d'utilisateur")
    email: EmailStr = Field(..., description="Adresse email")
    is_active: bool = Field(..., description="Compte actif")
    is_verified: bool = Field(..., description="Email vérifié")
    is_superuser: bool = Field(..., description="Administrateur")
    tenant_id: Optional[str] = Field(None, description="Identifiant du tenant")
    created_at: datetime = Field(..., description="Date de création")
    last_login: Optional[datetime] = Field(None, description="Dernière connexion")
    roles: list[RoleResponse] = Field(default_factory=list, description="Rôles de l'utilisateur")
    permissions: list[str] = Field(default_factory=list, description="Permissions de l'utilisateur")

    class Config:
        """Configuration Pydantic."""
        from_attributes = True


class MessageResponse(BaseModel):
    """Schéma de réponse pour les messages simples."""

    message: str = Field(..., description="Message")
    success: bool = Field(default=True, description="Succès de l'opération")


# ============================================
# Admin Schemas
# ============================================


class UserListResponse(BaseModel):
    """Schéma de réponse pour la liste des utilisateurs."""

    items: list[UserResponse] = Field(..., description="Liste des utilisateurs")
    total: int = Field(..., description="Nombre total d'utilisateurs")
    skip: int = Field(..., description="Offset")
    limit: int = Field(..., description="Limite")


class UpdateUserRequest(BaseModel):
    """Schéma de requête pour mettre à jour un utilisateur."""

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Nouveau nom d'utilisateur",
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Nouvelle adresse email",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Statut actif",
    )
    is_verified: Optional[bool] = Field(
        None,
        description="Statut vérifié",
    )
    is_superuser: Optional[bool] = Field(
        None,
        description="Statut administrateur",
    )
    tenant_id: Optional[str] = Field(
        None,
        description="Identifiant du tenant",
    )
