"""
Modèle Pydantic pour les documents MongoDB (Roles).

Ce module fournit un modèle de base extensible que le développeur
peut personnaliser en ajoutant ses propres champs via héritage.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class MongoRoleModel(BaseModel):
    """
    Modèle Pydantic pour les documents rôles MongoDB.

    Ce modèle peut être étendu par le développeur pour ajouter
    des champs personnalisés via héritage.

    Attributes:
        id: Identifiant unique (ObjectId généré par MongoDB)
        name: Nom unique du rôle
        display_name: Nom d'affichage
        description: Description du rôle
        permissions: Liste des permissions
        is_active: Rôle actif
        is_default: Rôle par défaut
        is_system: Rôle système
        priority: Priorité du rôle
        tenant_id: Identifiant du tenant (optionnel)
        created_at: Date de création
        updated_at: Date de mise à jour

    Example:
        Pour ajouter des champs personnalisés, créez une sous-classe:

        ```python
        from typing import Optional
        from pydantic import Field
        from alak_acl.roles.infrastructure.models import MongoRoleModel

        class CustomRoleModel(MongoRoleModel):
            department: Optional[str] = Field(None, max_length=100)
        ```
    """

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=2, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: List[str] = Field(default_factory=list)
    is_active: bool = True
    is_default: bool = False
    is_system: bool = False
    priority: int = Field(default=0, ge=0)
    tenant_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_mongo_dict(self, include_id: bool = False) -> dict:
        """
        Convertit le modèle en dictionnaire pour MongoDB.

        Args:
            include_id: Si True, inclut _id dans le dictionnaire

        Returns:
            Dictionnaire compatible MongoDB
        """
        data = self.model_dump(by_alias=True, exclude_none=False)
        if not include_id or data.get("_id") is None:
            data.pop("_id", None)
        return data

    @classmethod
    def from_mongo_dict(cls, data: dict) -> "MongoRoleModel":
        """
        Crée une instance depuis un document MongoDB.

        Args:
            data: Document MongoDB

        Returns:
            Instance du modèle
        """
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)


class MongoUserRoleModel(BaseModel):
    """
    Modèle pour les associations user-role dans MongoDB.

    Stocké dans une collection séparée ou embedded dans les utilisateurs.
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    role_id: str
    assigned_at: datetime = Field(default_factory=datetime.utcnow)

    def to_mongo_dict(self, include_id: bool = False) -> dict:
        """Convertit en dictionnaire MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=False)
        if not include_id or data.get("_id") is None:
            data.pop("_id", None)
        return data
