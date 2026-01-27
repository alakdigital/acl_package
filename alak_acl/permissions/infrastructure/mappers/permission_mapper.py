"""
Mapper pour convertir entre l'entité Permission et les modèles de persistance.

Ce mapper assure la conversion entre l'entité domaine Permission
et les modèles de base de données (SQL et MongoDB).

Il détecte automatiquement les colonnes personnalisées ajoutées
par héritage dans les sous-classes de modèles.
"""

from typing import Union, Dict, Any, TYPE_CHECKING, Optional, Type, Set

from alak_acl.permissions.domain.entities.permission import Permission
from alak_acl.permissions.infrastructure.models.mongo_model import MongoPermissionModel

# Import conditionnel pour éviter de charger SQLAlchemy si non utilisé
if TYPE_CHECKING:
    from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel


# Champs standards du modèle de base (ne sont pas des champs personnalisés)
STANDARD_PERMISSION_FIELDS: Set[str] = {
    'id', '_id', 'resource', 'action', 'name',
    'display_name', 'description', 'category',
    'is_active', 'is_system',
    'created_at', 'updated_at',
    # Champs techniques SQLAlchemy
    '_sa_instance_state',
}


def get_custom_columns_from_sql_model(model: Any) -> dict:
    """
    Extrait les colonnes personnalisées d'un modèle SQLAlchemy.

    Détecte les colonnes ajoutées par héritage qui ne font pas
    partie du modèle de base.

    Args:
        model: Instance du modèle SQLAlchemy

    Returns:
        Dictionnaire des colonnes personnalisées {nom: valeur}
    """
    extra = {}
    if hasattr(model, '__table__'):
        for column in model.__table__.columns:
            if column.name not in STANDARD_PERMISSION_FIELDS:
                extra[column.name] = getattr(model, column.name, None)
    return extra


def get_custom_fields_from_mongo_model(model: MongoPermissionModel) -> dict:
    """
    Extrait les champs personnalisés d'un modèle Pydantic MongoDB.

    Args:
        model: Instance du modèle Pydantic

    Returns:
        Dictionnaire des champs personnalisés {nom: valeur}
    """
    extra = {}
    # Accéder à model_fields depuis la classe pour éviter la dépréciation
    for field_name in type(model).model_fields:
        if field_name not in STANDARD_PERMISSION_FIELDS and field_name != '_id':
            extra[field_name] = getattr(model, field_name, None)
    return extra


def get_custom_fields_from_dict(data: dict) -> dict:
    """
    Extrait les champs personnalisés d'un dictionnaire MongoDB.

    Args:
        data: Document MongoDB

    Returns:
        Dictionnaire des champs personnalisés {nom: valeur}
    """
    return {
        key: value for key, value in data.items()
        if key not in STANDARD_PERMISSION_FIELDS
    }


class PermissionMapper:
    """
    Mapper pour la conversion entre Permission entity et modèles de persistance.

    Gère les conversions bidirectionnelles entre:
    - Permission (entité domaine)
    - SQLPermissionModel (PostgreSQL/MySQL)
    - MongoPermissionModel (MongoDB)
    - dict (documents MongoDB bruts)

    Détecte automatiquement les colonnes personnalisées ajoutées par héritage.
    """

    def __init__(
        self,
        sql_model_class: Optional[Type["SQLPermissionModel"]] = None,
        mongo_model_class: Type[MongoPermissionModel] = MongoPermissionModel,
    ):
        """
        Initialise le mapper.

        Args:
            sql_model_class: Classe du modèle SQL
            mongo_model_class: Classe du modèle MongoDB
        """
        self._sql_model_class = sql_model_class
        self._mongo_model_class = mongo_model_class

    def _get_sql_model_class(self) -> Type["SQLPermissionModel"]:
        """Retourne la classe SQL, avec import lazy si nécessaire."""
        if self._sql_model_class is None:
            from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
            self._sql_model_class = SQLPermissionModel
        return self._sql_model_class

    def to_entity(
        self,
        model: Union["SQLPermissionModel", MongoPermissionModel, Dict[str, Any], Any]
    ) -> Permission:
        """
        Convertit un modèle de persistance en entité Permission.

        Les colonnes personnalisées ajoutées par héritage sont
        automatiquement détectées et stockées dans extra_fields.

        Args:
            model: Modèle SQL, Mongo ou dictionnaire

        Returns:
            Entité Permission avec les champs personnalisés dans extra_fields
        """
        if isinstance(model, dict):
            # Document MongoDB
            extra_fields = get_custom_fields_from_dict(model)
            entity = Permission(
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
                extra_fields=extra_fields,
            )
            return entity

        elif isinstance(model, MongoPermissionModel):
            extra_fields = get_custom_fields_from_mongo_model(model)
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
                extra_fields=extra_fields,
            )

        # Modèle SQL (SQLAlchemy) - vérifie par duck typing
        elif hasattr(model, 'resource') and hasattr(model, 'action') and hasattr(model, 'is_system'):
            extra_fields = get_custom_columns_from_sql_model(model)
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
                extra_fields=extra_fields,
            )

        else:
            raise TypeError(f"Type non supporté: {type(model)}")

    def to_sql_model(
        self,
        entity: Permission,
        model_class: Optional[Type["SQLPermissionModel"]] = None,
    ) -> "SQLPermissionModel":
        """
        Convertit une entité Permission en modèle SQL.

        Les champs personnalisés dans extra_fields sont mappés
        aux colonnes correspondantes si elles existent dans le modèle.

        Args:
            entity: Entité Permission
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle SQLPermissionModel
        """
        cls = model_class or self._get_sql_model_class()

        model_data = {
            "id": entity.id,
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

        # Ajouter les champs personnalisés s'ils existent comme colonnes
        if entity.extra_fields and hasattr(cls, '__table__'):
            custom_column_names = {
                col.name for col in cls.__table__.columns
                if col.name not in STANDARD_PERMISSION_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_column_names:
                    model_data[key] = value

        return cls(**model_data)

    def to_mongo_model(
        self,
        entity: Permission,
        model_class: Optional[Type[MongoPermissionModel]] = None,
    ) -> MongoPermissionModel:
        """
        Convertit une entité Permission en modèle MongoDB.

        Les champs personnalisés dans extra_fields sont mappés
        aux champs correspondants si ils existent dans le modèle.

        Args:
            entity: Entité Permission
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle MongoPermissionModel
        """
        cls = model_class or self._mongo_model_class

        model_data = {
            "id": entity.id if entity.id else None,
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

        # Ajouter les champs personnalisés s'ils existent dans le modèle
        if entity.extra_fields:
            custom_field_names = {
                name for name in cls.model_fields
                if name not in STANDARD_PERMISSION_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_field_names:
                    model_data[key] = value

        return cls(**model_data)

    def to_mongo_dict(self, entity: Permission) -> Dict[str, Any]:
        """
        Convertit une entité Permission en dictionnaire MongoDB.

        Inclut automatiquement les champs personnalisés.

        Args:
            entity: Entité Permission

        Returns:
            Dictionnaire pour MongoDB
        """
        result = {
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

        # Ajouter les champs personnalisés directement au document
        if entity.extra_fields:
            result.update(entity.extra_fields)

        return result

    def update_sql_model(
        self,
        model: "SQLPermissionModel",
        entity: Permission,
    ) -> "SQLPermissionModel":
        """
        Met à jour un modèle SQL avec les valeurs d'une entité.

        Les champs personnalisés sont également mis à jour s'ils
        existent comme colonnes dans le modèle.

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

        # Mettre à jour les champs personnalisés
        if entity.extra_fields and hasattr(model, '__table__'):
            custom_column_names = {
                col.name for col in model.__table__.columns
                if col.name not in STANDARD_PERMISSION_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_column_names:
                    setattr(model, key, value)

        return model


# Instance globale par défaut
_default_mapper = PermissionMapper()


# Fonctions utilitaires pour import direct
def to_entity(model) -> Permission:
    """Alias pour PermissionMapper.to_entity."""
    return _default_mapper.to_entity(model)


def to_sql_model(entity: Permission) -> "SQLPermissionModel":
    """Alias pour PermissionMapper.to_sql_model."""
    return _default_mapper.to_sql_model(entity)


def to_mongo_model(entity: Permission) -> MongoPermissionModel:
    """Alias pour PermissionMapper.to_mongo_model."""
    return _default_mapper.to_mongo_model(entity)


def to_mongo_dict(entity: Permission) -> Dict[str, Any]:
    """Alias pour PermissionMapper.to_mongo_dict."""
    return _default_mapper.to_mongo_dict(entity)
