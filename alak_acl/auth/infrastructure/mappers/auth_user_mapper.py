"""
Mapper pour convertir AuthUser Entity <-> Models.

Ce mapper assure la conversion entre l'entité domaine AuthUser
et les modèles de base de données (SQL et MongoDB).

Il détecte automatiquement les colonnes personnalisées ajoutées
par héritage dans les sous-classes de modèles.
"""

from typing import Type, Union, Optional, TYPE_CHECKING, Any, Set

from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel

# Import conditionnel pour éviter de charger SQLAlchemy si non utilisé
if TYPE_CHECKING:
    from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel


# Champs standards du modèle de base (ne sont pas des champs personnalisés)
STANDARD_USER_FIELDS: Set[str] = {
    'id', '_id', 'username', 'email', 'hashed_password',
    'is_active', 'is_verified', 'is_superuser', 'tenant_id',
    'created_at', 'updated_at', 'last_login',
    # Champs techniques SQLAlchemy
    'roles', '_sa_instance_state',
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
    # Parcourir les colonnes de la table
    if hasattr(model, '__table__'):
        for column in model.__table__.columns:
            if column.name not in STANDARD_USER_FIELDS:
                extra[column.name] = getattr(model, column.name, None)
    return extra


def get_custom_fields_from_mongo_model(model: MongoAuthUserModel) -> dict:
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
        if field_name not in STANDARD_USER_FIELDS and field_name != '_id':
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
        if key not in STANDARD_USER_FIELDS
    }


class AuthUserMapper:
    """
    Mapper pour convertir entre l'entité AuthUser et les modèles DB.

    Assure la séparation entre la couche domaine et l'infrastructure.
    Détecte automatiquement les colonnes personnalisées ajoutées par héritage.

    Attributes:
        _sql_model_class: Classe du modèle SQL (peut être personnalisée)
        _mongo_model_class: Classe du modèle MongoDB (peut être personnalisée)
    """

    def __init__(
        self,
        sql_model_class: Optional[Type["SQLAuthUserModel"]] = None,
        mongo_model_class: Type[MongoAuthUserModel] = MongoAuthUserModel,
    ):
        """
        Initialise le mapper avec les classes de modèles personnalisées.

        Args:
            sql_model_class: Classe du modèle SQL (par défaut ou personnalisée)
            mongo_model_class: Classe du modèle MongoDB (par défaut ou personnalisée)
        """
        self._sql_model_class = sql_model_class
        self._mongo_model_class = mongo_model_class

    def _get_sql_model_class(self) -> Type["SQLAuthUserModel"]:
        """Retourne la classe SQL, avec import lazy si nécessaire."""
        if self._sql_model_class is None:
            from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel
            self._sql_model_class = SQLAuthUserModel
        return self._sql_model_class

    def to_entity(
        self,
        model: Union["SQLAuthUserModel", MongoAuthUserModel, dict, Any],
    ) -> AuthUser:
        """
        Convertit un modèle DB en entité domaine.

        Les colonnes personnalisées ajoutées par héritage sont
        automatiquement détectées et stockées dans extra_fields.

        Args:
            model: Modèle SQLAlchemy, Pydantic ou dictionnaire MongoDB

        Returns:
            Entité AuthUser avec les champs personnalisés dans extra_fields
        """
        if isinstance(model, dict):
            # Document MongoDB brut
            extra_fields = get_custom_fields_from_dict(model)
            return AuthUser(
                id=str(model["_id"]),
                username=model["username"],
                email=model["email"],
                hashed_password=model["hashed_password"],
                is_active=model.get("is_active", True),
                is_verified=model.get("is_verified", False),
                is_superuser=model.get("is_superuser", False),
                tenant_id=model.get("tenant_id"),
                created_at=model.get("created_at"),
                updated_at=model.get("updated_at"),
                last_login=model.get("last_login"),
                extra_fields=extra_fields,
            )

        if isinstance(model, MongoAuthUserModel):
            extra_fields = get_custom_fields_from_mongo_model(model)
            return AuthUser(
                id=str(model.id),
                username=model.username,
                email=model.email,
                hashed_password=model.hashed_password,
                is_active=model.is_active,
                is_verified=model.is_verified,
                is_superuser=model.is_superuser,
                tenant_id=model.tenant_id,
                created_at=model.created_at,
                updated_at=model.updated_at,
                last_login=model.last_login,
                extra_fields=extra_fields,
            )

        # Modèle SQL (SQLAlchemy) - vérifie par duck typing
        if hasattr(model, 'hashed_password') and hasattr(model, 'username'):
            extra_fields = get_custom_columns_from_sql_model(model)
            return AuthUser(
                id=str(model.id),
                username=model.username,
                email=model.email,
                hashed_password=model.hashed_password,
                is_active=model.is_active,
                is_verified=model.is_verified,
                is_superuser=model.is_superuser,
                tenant_id=model.tenant_id,
                created_at=model.created_at,
                updated_at=model.updated_at,
                last_login=model.last_login,
                extra_fields=extra_fields,
            )

        raise ValueError(f"Type de modèle non supporté: {type(model)}")

    def to_sql_model(
        self,
        entity: AuthUser,
        model_class: Optional[Type["SQLAuthUserModel"]] = None,
    ) -> "SQLAuthUserModel":
        """
        Convertit une entité en modèle SQLAlchemy.

        Les champs personnalisés dans extra_fields sont mappés
        aux colonnes correspondantes si elles existent dans le modèle.

        Args:
            entity: Entité AuthUser
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle SQLAlchemy
        """
        cls = model_class or self._get_sql_model_class()

        # Champs de base
        model_data = {
            "id": entity.id,
            "username": entity.username,
            "email": entity.email,
            "hashed_password": entity.hashed_password,
            "is_active": entity.is_active,
            "is_verified": entity.is_verified,
            "is_superuser": entity.is_superuser,
            "tenant_id": entity.tenant_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "last_login": entity.last_login,
        }

        # Ajouter les champs personnalisés s'ils existent comme colonnes
        if entity.extra_fields and hasattr(cls, '__table__'):
            custom_column_names = {
                col.name for col in cls.__table__.columns
                if col.name not in STANDARD_USER_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_column_names:
                    model_data[key] = value

        return cls(**model_data)

    def to_mongo_model(
        self,
        entity: AuthUser,
        model_class: Optional[Type[MongoAuthUserModel]] = None,
    ) -> MongoAuthUserModel:
        """
        Convertit une entité en modèle Pydantic pour MongoDB.

        Les champs personnalisés dans extra_fields sont mappés
        aux champs correspondants si ils existent dans le modèle.

        Args:
            entity: Entité AuthUser
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle Pydantic MongoDB
        """
        cls = model_class or self._mongo_model_class

        # Champs de base
        model_data = {
            "_id": entity.id,
            "username": entity.username,
            "email": entity.email,
            "hashed_password": entity.hashed_password,
            "is_active": entity.is_active,
            "is_verified": entity.is_verified,
            "is_superuser": entity.is_superuser,
            "tenant_id": entity.tenant_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "last_login": entity.last_login,
        }

        # Ajouter les champs personnalisés s'ils existent dans le modèle
        if entity.extra_fields:
            custom_field_names = {
                name for name in cls.model_fields
                if name not in STANDARD_USER_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_field_names:
                    model_data[key] = value

        return cls(**model_data)

    def to_mongo_dict(self, entity: AuthUser) -> dict:
        """
        Convertit une entité en dictionnaire pour MongoDB.

        Inclut automatiquement les champs personnalisés.

        Args:
            entity: Entité AuthUser

        Returns:
            Dictionnaire compatible MongoDB
        """
        result = {
            "username": entity.username,
            "email": entity.email,
            "hashed_password": entity.hashed_password,
            "is_active": entity.is_active,
            "is_verified": entity.is_verified,
            "is_superuser": entity.is_superuser,
            "tenant_id": entity.tenant_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "last_login": entity.last_login,
        }

        # Ajouter les champs personnalisés directement au document
        if entity.extra_fields:
            result.update(entity.extra_fields)

        return result

    def update_sql_model(
        self,
        model: "SQLAuthUserModel",
        entity: AuthUser,
    ) -> "SQLAuthUserModel":
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
        model.username = entity.username
        model.email = entity.email
        model.hashed_password = entity.hashed_password
        model.is_active = entity.is_active
        model.is_verified = entity.is_verified
        model.is_superuser = entity.is_superuser
        model.tenant_id = entity.tenant_id
        model.updated_at = entity.updated_at
        model.last_login = entity.last_login

        # Mettre à jour les champs personnalisés
        if entity.extra_fields and hasattr(model, '__table__'):
            custom_column_names = {
                col.name for col in model.__table__.columns
                if col.name not in STANDARD_USER_FIELDS
            }
            for key, value in entity.extra_fields.items():
                if key in custom_column_names:
                    setattr(model, key, value)

        return model


# Instance globale par défaut (pour compatibilité)
_default_mapper = AuthUserMapper()


# Fonctions statiques pour compatibilité avec l'ancien code
def to_entity(model: Union["SQLAuthUserModel", MongoAuthUserModel, dict, Any]) -> AuthUser:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_entity(model)


def to_sql_model(entity: AuthUser) -> "SQLAuthUserModel":
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_sql_model(entity)


def to_mongo_model(entity: AuthUser) -> MongoAuthUserModel:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_mongo_model(entity)


def to_mongo_dict(entity: AuthUser) -> dict:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_mongo_dict(entity)


def update_sql_model(model: "SQLAuthUserModel", entity: AuthUser) -> "SQLAuthUserModel":
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.update_sql_model(model, entity)
