"""
Modèle Pydantic pour les documents MongoDB.

Ce module fournit un modèle de base extensible que le développeur
peut personnaliser en ajoutant ses propres champs via héritage.
"""

from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class MongoAuthUserModel(BaseModel):
    """
    Modèle Pydantic de base pour les documents utilisateurs MongoDB.

    Ce modèle peut être étendu par le développeur pour ajouter
    des champs personnalisés via héritage.

    Attributes:
        id: Identifiant unique (ObjectId généré par MongoDB, stocké comme string)
        username: Nom d'utilisateur unique
        email: Email unique
        hashed_password: Mot de passe hashé
        is_active: Compte actif
        is_verified: Email vérifié
        is_superuser: Administrateur
        created_at: Date de création
        updated_at: Date de mise à jour
        last_login: Dernière connexion

    Example:
        Pour ajouter des champs personnalisés, créez une sous-classe:

        ```python
        from typing import Optional
        from pydantic import Field
        from alak_acl.auth.infrastructure.models import MongoAuthUserModel

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
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        },
    )

    # _id est optionnel car MongoDB le génère automatiquement lors de l'insertion
    id: Optional[str] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    def to_mongo_dict(self, include_id: bool = False) -> dict:
        """
        Convertit le modèle en dictionnaire pour MongoDB.

        Args:
            include_id: Si True, inclut _id dans le dictionnaire

        Returns:
            Dictionnaire compatible MongoDB
        """
        data = self.model_dump(by_alias=True, exclude_none=False)
        # Ne pas inclure _id lors de la création (MongoDB le génère)
        if not include_id or data.get("_id") is None:
            data.pop("_id", None)
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
            # Convertir ObjectId en string
            data["_id"] = str(data["_id"])
        return cls(**data)
