"""
Modèle Pydantic pour les permissions MongoDB.

Utilisé pour la validation et sérialisation des documents MongoDB.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MongoPermissionModel(BaseModel):
    """
    Modèle Pydantic pour les permissions MongoDB.

    Attributes:
        id: ID du document (alias pour _id MongoDB)
        resource: Ressource concernée
        action: Action autorisée
        name: Nom complet (resource:action)
        display_name: Nom d'affichage
        description: Description
        category: Catégorie pour regroupement
        is_active: Permission active
        is_system: Permission système
        created_at: Date de création
        updated_at: Date de mise à jour
    """

    id: Optional[str] = Field(default=None, alias="_id")
    resource: str = Field(..., max_length=50)
    action: str = Field(..., max_length=50)
    name: str = Field(..., max_length=101)
    display_name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=50)
    is_active: bool = Field(default=True)
    is_system: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None,
        },
    }

    def to_mongo_dict(self, include_id: bool = False) -> dict:
        """
        Convertit le modèle en dictionnaire pour MongoDB.

        Args:
            include_id: Inclure l'_id dans le dictionnaire

        Returns:
            Dictionnaire pour insertion/mise à jour MongoDB
        """
        data = self.model_dump(by_alias=True, exclude_none=False)

        # Ne pas inclure _id si None ou si non demandé
        if not include_id or data.get("_id") is None:
            data.pop("_id", None)

        return data

    @classmethod
    def from_mongo_doc(cls, doc: dict) -> "MongoPermissionModel":
        """
        Crée une instance depuis un document MongoDB.

        Args:
            doc: Document MongoDB

        Returns:
            Instance du modèle
        """
        if doc is None:
            return None

        # Convertir ObjectId en string
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

        return cls(**doc)
