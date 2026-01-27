"""
DTOs pour la feature Roles.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateRoleDTO(BaseModel):
    """DTO pour créer un nouveau rôle."""

    name: str = Field(..., min_length=2, max_length=50, description="Nom unique du rôle")
    display_name: Optional[str] = Field(None, max_length=100, description="Nom d'affichage")
    description: Optional[str] = Field(None, max_length=500, description="Description du rôle")
    permissions: List[str] = Field(default_factory=list, description="Liste des permissions")
    is_default: bool = Field(False, description="Rôle par défaut pour les nouveaux utilisateurs")
    priority: int = Field(0, ge=0, description="Priorité du rôle")
    tenant_id: Optional[str] = Field(None, description="Identifiant du tenant (optionnel)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "moderator",
                "display_name": "Modérateur",
                "description": "Peut modérer le contenu",
                "permissions": ["posts:read", "posts:update", "comments:delete"],
                "is_default": False,
                "priority": 50,
                "tenant_id": None,
            }
        }
    }


class UpdateRoleDTO(BaseModel):
    """DTO pour mettre à jour un rôle."""

    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)
    tenant_id: Optional[str] = Field(None, description="Identifiant du tenant")

    model_config = {
        "json_schema_extra": {
            "example": {
                "display_name": "Super Modérateur",
                "permissions": ["posts:*", "comments:*"],
                "priority": 75,
            }
        }
    }


class RoleResponseDTO(BaseModel):
    """DTO pour la réponse d'un rôle."""

    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    permissions: List[str]
    is_active: bool
    is_default: bool
    is_system: bool
    priority: int
    tenant_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "moderator",
                "display_name": "Modérateur",
                "description": "Peut modérer le contenu",
                "permissions": ["posts:read", "posts:update"],
                "is_active": True,
                "is_default": False,
                "is_system": False,
                "priority": 50,
                "tenant_id": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
    }


class RoleListResponseDTO(BaseModel):
    """DTO pour la liste des rôles avec pagination."""

    items: List[RoleResponseDTO]
    total: int
    skip: int
    limit: int


class AssignRoleDTO(BaseModel):
    """DTO pour assigner/retirer un rôle à un utilisateur."""

    user_id: str = Field(..., description="ID de l'utilisateur")
    role_id: str = Field(..., description="ID du rôle")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "role_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }


class AssignRolesDTO(BaseModel):
    """DTO pour assigner plusieurs rôles à un utilisateur."""

    user_id: str = Field(..., description="ID de l'utilisateur")
    role_ids: List[str] = Field(..., description="Liste des IDs de rôles")


class UserRolesResponseDTO(BaseModel):
    """DTO pour la réponse des rôles d'un utilisateur."""

    user_id: str
    roles: List[RoleResponseDTO]
    all_permissions: List[str] = Field(
        default_factory=list,
        description="Toutes les permissions de l'utilisateur (cumulées de tous ses rôles)",
    )


class AddPermissionDTO(BaseModel):
    """DTO pour ajouter une permission à un rôle."""

    permission: str = Field(..., min_length=1, max_length=100, description="Permission à ajouter")

    model_config = {
        "json_schema_extra": {
            "example": {
                "permission": "users:delete",
            }
        }
    }


class RemovePermissionDTO(BaseModel):
    """DTO pour retirer une permission d'un rôle."""

    permission: str = Field(..., min_length=1, max_length=100, description="Permission à retirer")
