"""
DTOs pour la feature Permissions.

Objets de transfert de données pour les opérations CRUD sur les permissions.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class CreatePermissionDTO(BaseModel):
    """
    DTO pour la création d'une permission.

    Attributes:
        resource: Ressource concernée (ex: "posts", "users")
        action: Action autorisée (ex: "read", "create", "update", "delete")
        display_name: Nom d'affichage lisible (optionnel)
        description: Description de la permission (optionnel)
        category: Catégorie pour regroupement (optionnel)
    """

    resource: str
    action: str 
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

    @field_validator("resource", "action")
    @classmethod
    def normalize_lowercase(cls, v: str) -> str:
        """Normalise en minuscules."""
        return v.lower().strip()
    
    
    @field_validator("resource")
    @classmethod
    def val_resource(cls, v: str) -> str:
        """Ressource concernée (ex: "posts", "users")."""
        if not v.strip():
            raise ValueError("Veuillez saisir la ressource")
        return v.lower().strip()
    

    @field_validator("action")
    @classmethod
    def val_action(cls, v: str) -> str:
        """Action autorisée (ex: "read", "create", "update", "delete", "*")"""
        if not v.strip():
            raise ValueError("Veuillez saisir l'action")
        if v.strip() == "*":
            return v
        return v.lower()
    

    @field_validator("display_name")
    @classmethod
    def val_display_name(cls, v: str) -> str:
        """Nom d'affichage (Ex: Créer des articles)"""
        if not v.strip():
            raise ValueError("Veuillez saisir le nom d'affichage")
        return v.strip()
    
    

    @field_validator("description")
    @classmethod
    def val_description(cls, v: str) -> str:
        """Description de la permission (Ex: "Permet de créer de nouveaux articles")"""
        if not v.strip():
            raise ValueError("Veuillez saisir l'action")
        return v.strip()
    


    model_config = {
        "json_schema_extra": {
            "example": {
                "resource": "posts",
                "action": "create",
                "display_name": "Créer des articles",
                "description": "Permet de créer de nouveaux articles",
                "category": "Content",
            }
        }
    }


class CreatePermissionFromNameDTO(BaseModel):
    """
    DTO pour créer une permission depuis un nom complet.

    Attributes:
        name: Nom au format "resource:action"
        display_name: Nom d'affichage lisible (optionnel)
        description: Description (optionnel)
        category: Catégorie (optionnel)
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=101,
        pattern=r"^[a-z0-9_-]+:[a-z0-9_*-]+$",
        description="Nom au format resource:action",
        examples=["posts:create", "users:read", "admin:*"],
    )
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)


class UpdatePermissionDTO(BaseModel):
    """
    DTO pour la mise à jour d'une permission.

    Tous les champs sont optionnels - seuls les champs fournis seront mis à jour.
    """

    display_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Nouveau nom d'affichage",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Nouvelle description",
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Nouvelle catégorie",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Activer/désactiver la permission",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "display_name": "Modifier des articles",
                "description": "Permet de modifier les articles existants",
                "is_active": True,
            }
        }
    }


class PermissionResponseDTO(BaseModel):
    """
    DTO pour la réponse d'une permission.

    Utilisé pour retourner les détails d'une permission.
    """

    id: str = Field(..., description="Identifiant unique")
    resource: str = Field(..., description="Ressource concernée")
    action: str = Field(..., description="Action autorisée")
    name: str = Field(..., description="Nom complet (resource:action)")
    display_name: Optional[str] = Field(None, description="Nom d'affichage")
    description: Optional[str] = Field(None, description="Description")
    category: Optional[str] = Field(None, description="Catégorie")
    is_active: bool = Field(..., description="Permission active")
    is_system: bool = Field(..., description="Permission système")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "resource": "posts",
                "action": "create",
                "name": "posts:create",
                "display_name": "Créer des articles",
                "description": "Permet de créer de nouveaux articles",
                "category": "Content",
                "is_active": True,
                "is_system": False,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": None,
            }
        },
    }


class PermissionListResponseDTO(BaseModel):
    """
    DTO pour la liste paginée des permissions.
    """

    permissions: List[PermissionResponseDTO] = Field(
        ...,
        description="Liste des permissions",
    )
    total: int = Field(..., description="Nombre total de permissions")
    skip: int = Field(..., description="Offset de pagination")
    limit: int = Field(..., description="Limite de pagination")

    model_config = {
        "json_schema_extra": {
            "example": {
                "permissions": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "resource": "posts",
                        "action": "create",
                        "name": "posts:create",
                        "display_name": "Créer des articles",
                        "description": "Permet de créer de nouveaux articles",
                        "category": "Content",
                        "is_active": True,
                        "is_system": False,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": None,
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 10,
            }
        }
    }


class AssignPermissionToRoleDTO(BaseModel):
    """
    DTO pour assigner une permission à un rôle.

    Attributes:
        permission_id: ID de la permission à assigner
    """

    permission_id: str = Field(
        ...,
        min_length=1,
        description="ID de la permission à assigner",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "permission_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }


class AssignPermissionsToRoleDTO(BaseModel):
    """
    DTO pour assigner plusieurs permissions à un rôle.

    Attributes:
        permission_ids: Liste des IDs de permissions à assigner
    """

    permission_ids: List[str] = Field(
        ...,
        min_length=1,
        description="Liste des IDs de permissions à assigner",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "permission_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "550e8400-e29b-41d4-a716-446655440001",
                ],
            }
        }
    }


class PermissionsByResourceDTO(BaseModel):
    """
    DTO pour grouper les permissions par ressource.
    """

    resource: str = Field(..., description="Nom de la ressource")
    permissions: List[PermissionResponseDTO] = Field(
        ...,
        description="Permissions de cette ressource",
    )


class PermissionsByCategoryDTO(BaseModel):
    """
    DTO pour grouper les permissions par catégorie.
    """

    category: str = Field(..., description="Nom de la catégorie")
    permissions: List[PermissionResponseDTO] = Field(
        ...,
        description="Permissions de cette catégorie",
    )
