"""
Modèle Pydantic pour les documents MongoDB (Roles).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, ConfigDict


class MongoRoleModel(BaseModel):
    """
    Modèle Pydantic pour les documents rôles MongoDB.

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
        created_at: Date de création
        updated_at: Date de mise à jour
        metadata: Métadonnées additionnelles

    Example:
        ```python
        from typing import Optional
        from pydantic import Field
        from fastapi_acl.roles.infrastructure.models import MongoRoleModel

        class CustomRoleModel(MongoRoleModel):
            department: Optional[str] = Field(None, max_length=100)
        ```
    """

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow",
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

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

    def get_extra_fields(self) -> Dict[str, Any]:
        """Retourne les valeurs des champs personnalisés."""
        standard_fields = {
            'id', 'name', 'display_name', 'description', 'permissions',
            'is_active', 'is_default', 'is_system', 'priority',
            'created_at', 'updated_at', 'metadata'
        }
        result = {}
        for field_name in self.model_fields:
            if field_name not in standard_fields and field_name != '_id':
                result[field_name] = getattr(self, field_name)
        return result

    @classmethod
    def get_custom_field_names(cls) -> list:
        """Retourne la liste des noms de champs personnalisés."""
        standard_fields = {
            'id', 'name', 'display_name', 'description', 'permissions',
            'is_active', 'is_default', 'is_system', 'priority',
            'created_at', 'updated_at', 'metadata'
        }
        return [
            name for name in cls.model_fields
            if name not in standard_fields
        ]


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


def create_mongo_role_model(
    extra_fields: Optional[Dict[str, tuple]] = None,
    model_name: str = "CustomMongoRoleModel",
) -> Type[MongoRoleModel]:
    """
    Factory pour créer un modèle MongoDB personnalisé dynamiquement.

    Args:
        extra_fields: Dictionnaire {nom: (type, Field())} des champs à ajouter
        model_name: Nom de la classe générée

    Returns:
        Classe de modèle personnalisée
    """
    annotations = {}
    defaults = {}

    if extra_fields:
        for field_name, (field_type, field_info) in extra_fields.items():
            annotations[field_name] = field_type
            defaults[field_name] = field_info

    namespace = {
        '__annotations__': {**MongoRoleModel.__annotations__, **annotations},
        '__module__': __name__,
        **defaults,
    }

    CustomModel = type(model_name, (MongoRoleModel,), namespace)

    return CustomModel
