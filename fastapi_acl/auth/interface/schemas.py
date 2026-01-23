"""
Schémas Pydantic pour l'API d'authentification.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================
# Request Schemas
# ============================================


class LoginRequest(BaseModel):
    """Schéma de requête pour la connexion."""

    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nom d'utilisateur ou email",
        examples=["john_doe", "john@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Mot de passe",
        examples=["mypassword123"],
    )


class RegisterRequest(BaseModel):
    """Schéma de requête pour l'inscription."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nom d'utilisateur unique",
        examples=["john_doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Adresse email unique",
        examples=["john@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Mot de passe (min 8 caractères)",
        examples=["MySecurePassword123"],
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Valide le format du nom d'utilisateur."""
        import re
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Le nom d'utilisateur ne peut contenir que des lettres, "
                "chiffres, tirets et underscores"
            )
        return v


class RefreshTokenRequest(BaseModel):
    """Schéma de requête pour rafraîchir un token."""

    refresh_token: str = Field(
        ...,
        description="Token de rafraîchissement",
    )


# ============================================
# Response Schemas
# ============================================


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

    id: UUID = Field(..., description="Identifiant unique")
    username: str = Field(..., description="Nom d'utilisateur")
    email: EmailStr = Field(..., description="Adresse email")
    is_active: bool = Field(..., description="Compte actif")
    is_verified: bool = Field(..., description="Email vérifié")
    is_superuser: bool = Field(..., description="Administrateur")
    created_at: datetime = Field(..., description="Date de création")
    last_login: Optional[datetime] = Field(None, description="Dernière connexion")

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

    users: list[UserResponse] = Field(..., description="Liste des utilisateurs")
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
