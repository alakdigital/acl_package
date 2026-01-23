"""
Modèle Pydantic pour les documents MongoDB.

Ce module fournit un modèle de base extensible que le développeur
peut personnaliser en ajoutant ses propres champs.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Type
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class MongoAuthUserModel(BaseModel):
    """
    Modèle Pydantic de base pour les documents utilisateurs MongoDB.

    Ce modèle peut être étendu par le développeur pour ajouter
    des champs personnalisés.

    Attributes:
        id: Identifiant unique UUID (stocké comme string dans MongoDB)
        username: Nom d'utilisateur unique
        email: Email unique
        hashed_password: Mot de passe hashé
        is_active: Compte actif
        is_verified: Email vérifié
        is_superuser: Administrateur
        created_at: Date de création
        updated_at: Date de mise à jour
        last_login: Dernière connexion
        extra_data: Champs personnalisés flexibles

    Example:
        Pour ajouter des champs personnalisés, créez une sous-classe:

        ```python
        from typing import Optional
        from pydantic import Field
        from fastapi_acl.auth.infrastructure.models import MongoAuthUserModel

        class CustomUserModel(MongoAuthUserModel):
            # Champs personnalisés
            phone: Optional[str] = Field(None, max_length=20)
            company: Optional[str] = Field(None, max_length=100)
            age: Optional[int] = Field(None, ge=0, le=150)
            department: Optional[str] = None
        ```
    """

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
        extra="allow",  # Permet les champs supplémentaires
    )

    id: UUID = Field(default_factory=uuid4, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    extra_data: Dict[str, Any] = Field(default_factory=dict)

    def to_mongo_dict(self) -> dict:
        """
        Convertit le modèle en dictionnaire pour MongoDB.

        Inclut automatiquement les champs personnalisés.

        Returns:
            Dictionnaire compatible MongoDB
        """
        data = self.model_dump(by_alias=True, exclude_none=False)
        # Convertir l'UUID en string pour MongoDB
        data["_id"] = str(data["_id"])
        return data

    @classmethod
    def from_mongo_dict(cls, data: dict) -> "MongoAuthUserModel":
        """
        Crée une instance depuis un document MongoDB.

        Args:
            data: Document MongoDB

        Returns:
            Instance du modèle
        """
        if "_id" in data:
            data["_id"] = UUID(data["_id"]) if isinstance(data["_id"], str) else data["_id"]
        return cls(**data)

    def get_extra_fields(self) -> Dict[str, Any]:
        """
        Retourne les valeurs des champs personnalisés définis dans la sous-classe.

        Returns:
            Dictionnaire des champs non-standard
        """
        standard_fields = {
            'id', 'username', 'email', 'hashed_password',
            'is_active', 'is_verified', 'is_superuser',
            'created_at', 'updated_at', 'last_login', 'extra_data'
        }
        result = {}
        for field_name in self.model_fields:
            if field_name not in standard_fields and field_name != '_id':
                result[field_name] = getattr(self, field_name)
        return result

    @classmethod
    def get_custom_field_names(cls) -> list:
        """
        Retourne la liste des noms de champs personnalisés.

        Returns:
            Liste des noms de champs ajoutés par le développeur
        """
        standard_fields = {
            'id', 'username', 'email', 'hashed_password',
            'is_active', 'is_verified', 'is_superuser',
            'created_at', 'updated_at', 'last_login', 'extra_data'
        }
        return [
            name for name in cls.model_fields
            if name not in standard_fields
        ]


def create_mongo_user_model(
    extra_fields: Optional[Dict[str, tuple]] = None,
    model_name: str = "CustomMongoAuthUserModel",
) -> Type[MongoAuthUserModel]:
    """
    Factory pour créer un modèle MongoDB personnalisé dynamiquement.

    Args:
        extra_fields: Dictionnaire {nom: (type, Field())} des champs à ajouter
        model_name: Nom de la classe générée

    Returns:
        Classe de modèle personnalisée

    Example:
        ```python
        from typing import Optional
        from pydantic import Field
        from fastapi_acl.auth.infrastructure.models import create_mongo_user_model

        CustomUser = create_mongo_user_model(
            extra_fields={
                "phone": (Optional[str], Field(None, max_length=20)),
                "company": (Optional[str], Field(None, max_length=100)),
                "age": (Optional[int], Field(None, ge=0)),
            }
        )
        ```
    """
    # Annotations de type pour les nouveaux champs
    annotations = {}
    defaults = {}

    if extra_fields:
        for field_name, (field_type, field_info) in extra_fields.items():
            annotations[field_name] = field_type
            defaults[field_name] = field_info

    # Créer la nouvelle classe
    namespace = {
        '__annotations__': {**MongoAuthUserModel.__annotations__, **annotations},
        '__module__': __name__,
        **defaults,
    }

    CustomModel = type(model_name, (MongoAuthUserModel,), namespace)

    return CustomModel
