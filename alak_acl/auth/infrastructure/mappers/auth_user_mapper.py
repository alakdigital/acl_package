"""
Mapper pour convertir AuthUser Entity <-> Models.

Ce mapper gère automatiquement les champs personnalisés
définis par le développeur.
"""

from typing import Type, Union, Optional

from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel
from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel




class AuthUserMapper:
    """
    Mapper pour convertir entre l'entité AuthUser et les modèles DB.

    Assure la séparation entre la couche domaine et l'infrastructure.
    Gère automatiquement les champs personnalisés.

    Attributes:
        _sql_model_class: Classe du modèle SQL (peut être personnalisée)
        _mongo_model_class: Classe du modèle MongoDB (peut être personnalisée)
        _custom_field_names: Liste des noms de champs personnalisés
    """

    # Champs standards qui ne sont pas des champs personnalisés
    STANDARD_FIELDS = {
        'id', '_id', 'username', 'email', 'hashed_password',
        'is_active', 'is_verified', 'is_superuser',
        'created_at', 'updated_at', 'last_login', 'extra_data'
    }

    def __init__(
        self,
        sql_model_class: Type[SQLAuthUserModel] = SQLAuthUserModel,
        mongo_model_class: Type[MongoAuthUserModel] = MongoAuthUserModel,
        custom_field_names: Optional[list] = None,
    ):
        """
        Initialise le mapper avec les classes de modèles personnalisées.

        Args:
            sql_model_class: Classe du modèle SQL (par défaut ou personnalisée)
            mongo_model_class: Classe du modèle MongoDB (par défaut ou personnalisée)
            custom_field_names: Liste explicite des noms de champs personnalisés
        """
        self._sql_model_class = sql_model_class
        self._mongo_model_class = mongo_model_class
        self._custom_field_names = custom_field_names or []

    def to_entity(
        self,
        model: Union[SQLAuthUserModel, MongoAuthUserModel, dict],
    ) -> AuthUser:
        """
        Convertit un modèle DB en entité domaine.

        Les champs personnalisés sont stockés dans extra_fields.

        Args:
            model: Modèle SQLAlchemy, Pydantic ou dictionnaire MongoDB

        Returns:
            Entité AuthUser avec les champs personnalisés dans extra_fields
        """
        extra_fields = {}

        if isinstance(model, dict):
            # Document MongoDB brut
            # Extraire les champs personnalisés
            for key, value in model.items():
                if key not in self.STANDARD_FIELDS:
                    extra_fields[key] = value

            # Combiner avec extra_data si présent
            if "extra_data" in model and model["extra_data"]:
                extra_fields.update(model["extra_data"])

            return AuthUser(
                id=str(model["_id"]),
                username=model["username"],
                email=model["email"],
                hashed_password=model["hashed_password"],
                is_active=model.get("is_active", True),
                is_verified=model.get("is_verified", False),
                is_superuser=model.get("is_superuser", False),
                created_at=model.get("created_at"),
                updated_at=model.get("updated_at"),
                last_login=model.get("last_login"),
                extra_fields=extra_fields,
            )

        if isinstance(model, SQLAuthUserModel):
            # Extraire les colonnes personnalisées du modèle SQL
            extra_fields = model.get_extra_columns()

            # Combiner avec extra_data JSON si présent
            if model.extra_data:
                extra_fields.update(model.extra_data)

            return AuthUser(
                id=str(model.id),
                username=model.username,
                email=model.email,
                hashed_password=model.hashed_password,
                is_active=model.is_active,
                is_verified=model.is_verified,
                is_superuser=model.is_superuser,
                created_at=model.created_at,
                updated_at=model.updated_at,
                last_login=model.last_login,
                extra_fields=extra_fields,
            )

        if isinstance(model, MongoAuthUserModel):
            # Extraire les champs personnalisés du modèle Pydantic
            extra_fields = model.get_extra_fields()

            # Combiner avec extra_data si présent
            if model.extra_data:
                extra_fields.update(model.extra_data)

            return AuthUser(
                id=str(model.id),
                username=model.username,
                email=model.email,
                hashed_password=model.hashed_password,
                is_active=model.is_active,
                is_verified=model.is_verified,
                is_superuser=model.is_superuser,
                created_at=model.created_at,
                updated_at=model.updated_at,
                last_login=model.last_login,
                extra_fields=extra_fields,
            )

        raise ValueError(f"Type de modèle non supporté: {type(model)}")

    def to_sql_model(
        self,
        entity: AuthUser,
        model_class: Optional[Type[SQLAuthUserModel]] = None,
    ) -> SQLAuthUserModel:
        """
        Convertit une entité en modèle SQLAlchemy.

        Les champs personnalisés sont mappés si le modèle les supporte,
        sinon ils sont stockés dans extra_data (JSON).

        Args:
            entity: Entité AuthUser
            model_class: Classe de modèle personnalisée (optionnel)

        Returns:
            Modèle SQLAlchemy
        """
        cls = model_class or self._sql_model_class

        # Champs de base
        model_data = {
            "id": entity.id,
            "username": entity.username,
            "email": entity.email,
            "hashed_password": entity.hashed_password,
            "is_active": entity.is_active,
            "is_verified": entity.is_verified,
            "is_superuser": entity.is_superuser,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "last_login": entity.last_login,
        }

        # Gérer les champs personnalisés
        extra_data_json = {}
        custom_columns = cls.get_custom_column_names() if hasattr(cls, 'get_custom_column_names') else []

        for key, value in entity.extra_fields.items():
            if key in custom_columns:
                # Le champ existe comme colonne dans le modèle
                model_data[key] = value
            else:
                # Stocker dans extra_data JSON
                extra_data_json[key] = value

        model_data["extra_data"] = extra_data_json if extra_data_json else None

        return cls(**model_data)

    def to_mongo_model(
        self,
        entity: AuthUser,
        model_class: Optional[Type[MongoAuthUserModel]] = None,
    ) -> MongoAuthUserModel:
        """
        Convertit une entité en modèle Pydantic pour MongoDB.

        Les champs personnalisés sont mappés si le modèle les supporte,
        sinon ils sont stockés dans extra_data.

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
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "last_login": entity.last_login,
        }

        # Gérer les champs personnalisés
        extra_data = {}
        custom_fields = cls.get_custom_field_names() if hasattr(cls, 'get_custom_field_names') else []

        for key, value in entity.extra_fields.items():
            if key in custom_fields:
                # Le champ existe dans le modèle Pydantic
                model_data[key] = value
            else:
                # Stocker dans extra_data
                extra_data[key] = value

        model_data["extra_data"] = extra_data

        return cls(**model_data)

    def to_mongo_dict(self, entity: AuthUser) -> dict:
        """
        Convertit une entité en dictionnaire pour MongoDB.

        Inclut tous les champs personnalisés.

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
        model: SQLAuthUserModel,
        entity: AuthUser,
    ) -> SQLAuthUserModel:
        """
        Met à jour un modèle SQL avec les données d'une entité.

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
        model.updated_at = entity.updated_at
        model.last_login = entity.last_login

        # Mettre à jour les champs personnalisés
        custom_columns = model.get_custom_column_names() if hasattr(model, 'get_custom_column_names') else []
        extra_data_json = {}

        for key, value in entity.extra_fields.items():
            if key in custom_columns:
                setattr(model, key, value)
            else:
                extra_data_json[key] = value

        model.extra_data = extra_data_json if extra_data_json else None

        return model


# Instance globale par défaut (pour compatibilité)
_default_mapper = AuthUserMapper()


# Fonctions statiques pour compatibilité avec l'ancien code
def to_entity(model: Union[SQLAuthUserModel, MongoAuthUserModel, dict]) -> AuthUser:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_entity(model)


def to_sql_model(entity: AuthUser) -> SQLAuthUserModel:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_sql_model(entity)


def to_mongo_model(entity: AuthUser) -> MongoAuthUserModel:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_mongo_model(entity)


def to_mongo_dict(entity: AuthUser) -> dict:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.to_mongo_dict(entity)


def update_sql_model(model: SQLAuthUserModel, entity: AuthUser) -> SQLAuthUserModel:
    """Fonction de compatibilité - utilise le mapper par défaut."""
    return _default_mapper.update_sql_model(model, entity)
