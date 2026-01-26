"""
Mapper pour convertir entre l'entité Permission et les modèles de persistance.
"""

from typing import Union, Dict, Any, TYPE_CHECKING

from alak_acl.permissions.domain.entities.permission import Permission
from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel

# Import conditionnel pour éviter de charger SQLAlchemy si non utilisé
if TYPE_CHECKING:
    from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel


class PermissionMapper:
    """
    Mapper pour la conversion entre Permission entity et modèles de persistance.

    Gère les conversions bidirectionnelles entre:
    - Permission (entité domaine)
    - SQLPermissionModel (PostgreSQL/MySQL)
    - MongoPermissionModel (MongoDB)
    - dict (documents MongoDB bruts)
    """

    @staticmethod
    def to_entity(
        model: Union["SQLPermissionModel", MongoPermissionModel, Dict[str, Any], Any]
    ) -> Permission:
        """
        Convertit un modèle de persistance en entité Permission.

        Args:
            model: Modèle SQL, Mongo ou dictionnaire

        Returns:
            Entité Permission
        """
        if isinstance(model, dict):
            # Document MongoDB
            return Permission(
                id=str(model.get("_id", model.get("id", ""))),
                resource=model["resource"],
                action=model["action"],
                display_name=model.get("display_name"),
                description=model.get("description"),
                category=model.get("category"),
                is_active=model.get("is_active", True),
                is_system=model.get("is_system", False),
                created_at=model.get("created_at"),
                updated_at=model.get("updated_at"),
            )

        elif isinstance(model, MongoPermissionModel):
            return Permission(
                id=model.id or "",
                resource=model.resource,
                action=model.action,
                display_name=model.display_name,
                description=model.description,
                category=model.category,
                is_active=model.is_active,
                is_system=model.is_system,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )

        # Modèle SQL (SQLAlchemy) - vérifie par duck typing
        elif hasattr(model, 'resource') and hasattr(model, 'action') and hasattr(model, 'is_system'):
            return Permission(
                id=model.id,
                resource=model.resource,
                action=model.action,
                display_name=model.display_name,
                description=model.description,
                category=model.category,
                is_active=model.is_active,
                is_system=model.is_system,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )

        else:
            raise TypeError(f"Type non supporté: {type(model)}")

    @staticmethod
    def to_sql_model(entity: Permission) -> "SQLPermissionModel":
        """
        Convertit une entité Permission en modèle SQL.

        Args:
            entity: Entité Permission

        Returns:
            Modèle SQLPermissionModel
        """
        from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
        return SQLPermissionModel(
            id=entity.id,
            resource=entity.resource,
            action=entity.action,
            name=entity.name,
            display_name=entity.display_name,
            description=entity.description,
            category=entity.category,
            is_active=entity.is_active,
            is_system=entity.is_system,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_mongo_model(entity: Permission) -> MongoPermissionModel:
        """
        Convertit une entité Permission en modèle MongoDB.

        Args:
            entity: Entité Permission

        Returns:
            Modèle MongoPermissionModel
        """
        return MongoPermissionModel(
            id=entity.id if entity.id else None,
            resource=entity.resource,
            action=entity.action,
            name=entity.name,
            display_name=entity.display_name,
            description=entity.description,
            category=entity.category,
            is_active=entity.is_active,
            is_system=entity.is_system,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_mongo_dict(entity: Permission) -> Dict[str, Any]:
        """
        Convertit une entité Permission en dictionnaire MongoDB.

        Args:
            entity: Entité Permission

        Returns:
            Dictionnaire pour MongoDB
        """
        return {
            "resource": entity.resource,
            "action": entity.action,
            "name": entity.name,
            "display_name": entity.display_name,
            "description": entity.description,
            "category": entity.category,
            "is_active": entity.is_active,
            "is_system": entity.is_system,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    @staticmethod
    def update_sql_model(
        model: "SQLPermissionModel",
        entity: Permission,
    ) -> "SQLPermissionModel":
        """
        Met à jour un modèle SQL avec les valeurs d'une entité.

        Args:
            model: Modèle SQL à mettre à jour
            entity: Entité avec les nouvelles valeurs

        Returns:
            Modèle SQL mis à jour
        """
        model.display_name = entity.display_name
        model.description = entity.description
        model.category = entity.category
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        return model


# Fonctions utilitaires pour import direct
def to_entity(model) -> Permission:
    """Alias pour PermissionMapper.to_entity."""
    return PermissionMapper.to_entity(model)


def to_sql_model(entity: Permission) -> "SQLPermissionModel":
    """Alias pour PermissionMapper.to_sql_model."""
    return PermissionMapper.to_sql_model(entity)


def to_mongo_model(entity: Permission) -> MongoPermissionModel:
    """Alias pour PermissionMapper.to_mongo_model."""
    return PermissionMapper.to_mongo_model(entity)


def to_mongo_dict(entity: Permission) -> Dict[str, Any]:
    """Alias pour PermissionMapper.to_mongo_dict."""
    return PermissionMapper.to_mongo_dict(entity)
