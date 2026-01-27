"""
Mapper pour convertir Role Entity <-> Models.

Ce mapper assure la conversion entre l'entité domaine Role
et les modèles de base de données (SQL et MongoDB).

Il détecte automatiquement les colonnes personnalisées ajoutées
par héritage dans les sous-classes de modèles.
"""

from typing import Any, Type, Union, Optional, TYPE_CHECKING, Set

from alak_acl.roles.domain.entities.role import Role
from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel

# Import conditionnel pour éviter de charger SQLAlchemy si non utilisé
if TYPE_CHECKING:
    from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel


# Champs standards du modèle de base (ne sont pas des champs personnalisés)
STANDARD_ROLE_FIELDS: Set[str] = {
    'id', '_id', 'name', 'display_name', 'description', 'permissions',
    'is_active', 'is_default', 'is_system', 'priority',
    'created_at', 'updated_at',
    # Champs techniques SQLAlchemy
    'users', '_sa_instance_state',
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
            if column.name not in STANDARD_ROLE_FIELDS:
                extra[column.name] = getattr(model, column.name, None)
    return extra


def get_custom_fields_from_mongo_model(model: MongoRoleModel) -> dict:
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
        if field_name not in STANDARD_ROLE_FIELDS and field_name != '_id':
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
        if key not in STANDARD_ROLE_FIELDS
    }


class RoleMapper:
    """
    Mapper pour convertir entre l'entité Role et les modèles DB.

    Assure la séparation entre la couche domaine et l'infrastructure.
    Détecte automatiquement les colonnes personnalisées ajoutées par héritage.
    """

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

        Les colonnes personnalisées ajoutées par héritage sont
        automatiquement détectées et stockées dans extra_fields.

        Args:
            model: Modèle SQLAlchemy, Pydantic ou dictionnaire MongoDB

        Returns:
            Entité Role avec les champs personnalisés dans extra_fields
        """
        if isinstance(model, dict):
            # Document MongoDB brut
            extra_fields = get_custom_fields_from_dict(model)
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
                extra_fields=extra_fields,
            )

        if isinstance(model, MongoRoleModel):
            extra_fields = get_custom_fields_from_mongo_model(model)
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
                extra_fields=extra_fields,
            )

        # Modèle SQL (SQLAlchemy) - vérifie par duck typing
        if hasattr(model, 'permissions') and hasattr(model, 'is_system'):
            extra_fields = get_custom_columns_from_sql_model(model)
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
                extra_fields=extra_fields,
            )

        raise ValueError(f"Type de modèle non supporté: {type(model)}")

    def to_sql_model(
        self,
        entity: Role,
        model_class: Optional[Type["SQLRoleModel"]] = None,
    ) -> "SQLRoleModel":
        """
        Convertit une entité en modèle SQLAlchemy.

        Les champs personnalisés dans extra_fields sont mappés
        aux colonnes correspondantes si elles existent dans le modèle.

        Args:
            entity: Entité Role
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle SQLAlchemy
        """
        cls = model_class or self._get_sql_model_class()

        # Champs de base
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
        }

        # Ajouter les champs personnalisés s'ils existent comme colonnes
        if entity.extra_fields and hasattr(cls, '__table__'):
            custom_column_names = {
                col.name for col in cls.__table__.columns
                if col.name not in STANDARD_ROLE_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_column_names:
                    model_data[key] = value

        return cls(**model_data)

    def to_mongo_model(
        self,
        entity: Role,
        model_class: Optional[Type[MongoRoleModel]] = None,
    ) -> MongoRoleModel:
        """
        Convertit une entité en modèle Pydantic pour MongoDB.

        Les champs personnalisés dans extra_fields sont mappés
        aux champs correspondants si ils existent dans le modèle.

        Args:
            entity: Entité Role
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle Pydantic MongoDB
        """
        cls = model_class or self._mongo_model_class

        # Champs de base
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
        }

        if entity.id:
            model_data["_id"] = entity.id

        # Ajouter les champs personnalisés s'ils existent dans le modèle
        if entity.extra_fields:
            custom_field_names = {
                name for name in cls.model_fields
                if name not in STANDARD_ROLE_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_field_names:
                    model_data[key] = value

        return cls(**model_data)

    def to_mongo_dict(self, entity: Role) -> dict:
        """
        Convertit une entité en dictionnaire pour MongoDB.

        Inclut automatiquement les champs personnalisés.

        Args:
            entity: Entité Role

        Returns:
            Dictionnaire compatible MongoDB
        """
        result = {
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
        }

        # Ajouter les champs personnalisés directement au document
        if entity.extra_fields:
            result.update(entity.extra_fields)

        return result

    def update_sql_model(
        self,
        model: "SQLRoleModel",
        entity: Role,
    ) -> "SQLRoleModel":
        """
        Met à jour un modèle SQL avec les données d'une entité.

        Les champs personnalisés sont également mis à jour s'ils
        existent comme colonnes dans le modèle.

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

        # Mettre à jour les champs personnalisés
        if entity.extra_fields and hasattr(model, '__table__'):
            custom_column_names = {
                col.name for col in model.__table__.columns
                if col.name not in STANDARD_ROLE_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_column_names:
                    setattr(model, key, value)

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
