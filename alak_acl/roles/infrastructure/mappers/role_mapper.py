"""
Mapper pour convertir Role Entity <-> Models.
"""

from typing import Any, Dict, Type, Union, Optional, TYPE_CHECKING

from alak_acl.roles.domain.entities.role import Role
from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel

# Import conditionnel pour éviter de charger SQLAlchemy si non utilisé
if TYPE_CHECKING:
    from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel


class RoleMapper:
    """
    Mapper pour convertir entre l'entité Role et les modèles DB.

    Assure la séparation entre la couche domaine et l'infrastructure.
    """

    STANDARD_FIELDS = {
        'id', '_id', 'name', 'display_name', 'description', 'permissions',
        'is_active', 'is_default', 'is_system', 'priority',
        'created_at', 'updated_at', 'metadata', 'metadata_'
    }

    def __init__(
        self,
        sql_model_class: Optional[Type["SQLRoleModel"]] = None,
        mongo_model_class: Type[MongoRoleModel] = MongoRoleModel,
    ):
        """
        Initialise le mapper.

        Args:
            sql_model_class: Classe du modèle SQL
            mongo_model_class: Classe du modèle MongoDB
        """
        self._sql_model_class = sql_model_class
        self._mongo_model_class = mongo_model_class

    def _get_sql_model_class(self) -> Type["SQLRoleModel"]:
        """Retourne la classe SQL, avec import lazy si nécessaire."""
        if self._sql_model_class is None:
            from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel
            self._sql_model_class = SQLRoleModel
        return self._sql_model_class

    def to_entity(
        self,
        model: Union["SQLRoleModel", MongoRoleModel, dict, Any],
    ) -> Role:
        """
        Convertit un modèle DB en entité domaine.

        Args:
            model: Modèle SQLAlchemy, Pydantic ou dictionnaire MongoDB

        Returns:
            Entité Role
        """
        if isinstance(model, dict):
            # Document MongoDB brut
            return Role(
                id=str(model["_id"]),
                name=model["name"],
                display_name=model.get("display_name"),
                description=model.get("description"),
                permissions=model.get("permissions", []),
                is_active=model.get("is_active", True),
                is_default=model.get("is_default", False),
                is_system=model.get("is_system", False),
                priority=model.get("priority", 0),
                created_at=model.get("created_at"),
                updated_at=model.get("updated_at"),
                metadata=model.get("metadata", {}),
            )

        if isinstance(model, MongoRoleModel):
            return Role(
                id=str(model.id) if model.id else None,
                name=model.name,
                display_name=model.display_name,
                description=model.description,
                permissions=model.permissions or [],
                is_active=model.is_active,
                is_default=model.is_default,
                is_system=model.is_system,
                priority=model.priority,
                created_at=model.created_at,
                updated_at=model.updated_at,
                metadata=model.metadata or {},
            )

        # Modèle SQL (SQLAlchemy) - vérifie par duck typing
        if hasattr(model, 'metadata_') and hasattr(model, 'permissions'):
            return Role(
                id=str(model.id),
                name=model.name,
                display_name=model.display_name,
                description=model.description,
                permissions=model.permissions or [],
                is_active=model.is_active,
                is_default=model.is_default,
                is_system=model.is_system,
                priority=model.priority,
                created_at=model.created_at,
                updated_at=model.updated_at,
                metadata=model.metadata_ or {},
            )

        raise ValueError(f"Type de modèle non supporté: {type(model)}")

    def to_sql_model(
        self,
        entity: Role,
        model_class: Optional[Type["SQLRoleModel"]] = None,
    ) -> "SQLRoleModel":
        """
        Convertit une entité en modèle SQLAlchemy.

        Args:
            entity: Entité Role
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle SQLAlchemy
        """
        cls = model_class or self._get_sql_model_class()

        model_data = {
            "id": entity.id,
            "name": entity.name,
            "display_name": entity.display_name,
            "description": entity.description,
            "permissions": entity.permissions,
            "is_active": entity.is_active,
            "is_default": entity.is_default,
            "is_system": entity.is_system,
            "priority": entity.priority,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "metadata_": entity.metadata,
        }

        return cls(**model_data)

    def to_mongo_model(
        self,
        entity: Role,
        model_class: Optional[Type[MongoRoleModel]] = None,
    ) -> MongoRoleModel:
        """
        Convertit une entité en modèle Pydantic pour MongoDB.

        Args:
            entity: Entité Role
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle Pydantic MongoDB
        """
        cls = model_class or self._mongo_model_class

        model_data = {
            "name": entity.name,
            "display_name": entity.display_name,
            "description": entity.description,
            "permissions": entity.permissions,
            "is_active": entity.is_active,
            "is_default": entity.is_default,
            "is_system": entity.is_system,
            "priority": entity.priority,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "metadata": entity.metadata,
        }

        if entity.id:
            model_data["_id"] = entity.id

        return cls(**model_data)

    def to_mongo_dict(self, entity: Role) -> dict:
        """
        Convertit une entité en dictionnaire pour MongoDB.

        Args:
            entity: Entité Role

        Returns:
            Dictionnaire compatible MongoDB
        """
        return {
            "name": entity.name,
            "display_name": entity.display_name,
            "description": entity.description,
            "permissions": entity.permissions,
            "is_active": entity.is_active,
            "is_default": entity.is_default,
            "is_system": entity.is_system,
            "priority": entity.priority,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "metadata": entity.metadata,
        }

    def update_sql_model(
        self,
        model: "SQLRoleModel",
        entity: Role,
    ) -> "SQLRoleModel":
        """
        Met à jour un modèle SQL avec les données d'une entité.

        Args:
            model: Modèle SQLAlchemy existant
            entity: Entité avec les nouvelles données

        Returns:
            Modèle mis à jour
        """
        model.name = entity.name
        model.display_name = entity.display_name
        model.description = entity.description
        model.permissions = entity.permissions
        model.is_active = entity.is_active
        model.is_default = entity.is_default
        model.is_system = entity.is_system
        model.priority = entity.priority
        model.updated_at = entity.updated_at
        model.metadata_ = entity.metadata

        return model


# Instance globale par défaut
_default_mapper = RoleMapper()


def to_entity(model: Union["SQLRoleModel", MongoRoleModel, dict, Any]) -> Role:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_entity(model)


def to_sql_model(entity: Role) -> "SQLRoleModel":
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_sql_model(entity)


def to_mongo_model(entity: Role) -> MongoRoleModel:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_mongo_model(entity)


def to_mongo_dict(entity: Role) -> dict:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_mongo_dict(entity)
