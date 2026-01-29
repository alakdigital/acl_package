"""
Repository MongoDB pour l'authentification.

Supporte les champs personnalisés ajoutés directement aux documents.
"""

from typing import Any, Optional, List, Type

from bson import ObjectId


from alak_acl.auth.application.interface.auth_repository import IAuthRepository
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.infrastructure.mappers.auth_user_mapper import AuthUserMapper
from alak_acl.auth.infrastructure.models.mongo_model import MongoAuthUserModel
from alak_acl.shared.database.mongodb import MongoDBDatabase
from alak_acl.shared.exceptions import UserAlreadyExistsError, UserNotFoundError
from alak_acl.shared.logging import logger


class MongoDBAuthRepository(IAuthRepository):
    """
    Implémentation du repository d'authentification pour MongoDB.

    Utilise motor pour les opérations asynchrones.
    Supporte les champs personnalisés qui sont ajoutés directement aux documents.

    Attributes:
        db: Instance de connexion MongoDB
        collection_name: Nom de la collection
        model_class: Classe du modèle Pydantic (optionnel)
        mapper: Instance du mapper

    Example:
        ```python
        # Avec modèle personnalisé
        from typing import Optional
        from pydantic import Field
        from alak_acl.auth.infrastructure.models import MongoAuthUserModel

        class CustomUserModel(MongoAuthUserModel):
            phone: Optional[str] = Field(None, max_length=20)
            company: Optional[str] = Field(None, max_length=100)

        repo = MongoDBAuthRepository(
            db=database,
            collection_name="users",
            model_class=CustomUserModel,
        )
        ```
    """

    def __init__(
        self,
        db: MongoDBDatabase,
        collection_name: str = "auth_users",
        model_class: Type[MongoAuthUserModel] = MongoAuthUserModel,
        mapper: Optional[AuthUserMapper] = None,
    ):
        """
        Initialise le repository.

        Args:
            db: Instance de MongoDBDatabase
            collection_name: Nom de la collection MongoDB
            model_class: Classe du modèle Pydantic (par défaut ou personnalisée)
            mapper: Instance du mapper personnalisée (optionnel)
        """
        self._db = db
        self._collection_name = collection_name
        self._model_class = model_class
        self._mapper = mapper or AuthUserMapper(mongo_model_class=model_class)

    @property
    def _collection(self):
        """Retourne la collection MongoDB."""
        return self._db.get_collection(self._collection_name)

    @property
    def collection_name(self) -> str:
        """Retourne le nom de la collection."""
        return self._collection_name

    @property
    def model_class(self) -> Type[MongoAuthUserModel]:
        """Retourne la classe du modèle utilisé."""
        return self._model_class

    async def create_user(self, user: AuthUser) -> AuthUser:
        """
        Crée un nouvel utilisateur.

        Les champs personnalisés dans extra_fields sont automatiquement
        ajoutés au document MongoDB. L'_id est généré automatiquement par MongoDB.
        """
        # Vérifier l'unicité
        existing = await self._collection.find_one({
            "$or": [
                {"username": user.username},
                {"email": user.email}
            ]
        })
        if existing:
            raise UserAlreadyExistsError(
                "__all__",
                "Un utilisateur avec ce username ou email existe déjà"
            )

        doc = self._mapper.to_mongo_dict(user)
        # Ne pas inclure _id - MongoDB le génère automatiquement
        doc.pop("_id", None)

        result = await self._collection.insert_one(doc)
        # Récupérer l'ID généré par MongoDB
        user.id = str(result.inserted_id)

        logger.debug(f"Utilisateur créé: {user.username} (id: {user.id})")
        return user

    async def get_by_id(self, user_id: str) -> Optional[AuthUser]:
        """Récupère un utilisateur par son ID (ObjectId string)."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(user_id)})
            if doc:
                return self._mapper.to_entity(doc)
        except Exception:
            pass
        return None

    async def get_by_username(self, username: str) -> Optional[AuthUser]:
        """Récupère un utilisateur par son username."""
        doc = await self._collection.find_one({"username": username})
        if doc:
            return self._mapper.to_entity(doc)
        return None

    async def get_by_email(self, email: str) -> Optional[AuthUser]:
        """Récupère un utilisateur par son email."""
        doc = await self._collection.find_one({"email": email})
        if doc:
            return self._mapper.to_entity(doc)
        return None

    async def update_user(self, user: AuthUser) -> AuthUser:
        """
        Met à jour un utilisateur.

        Les champs personnalisés dans extra_fields sont automatiquement
        mis à jour dans le document MongoDB.
        """
        doc = self._mapper.to_mongo_dict(user)
        result = await self._collection.update_one(
            {"_id": ObjectId(user.id)},
            {'$set': doc}
        )

        if result.matched_count == 0:
            raise UserNotFoundError("id", f"Utilisateur non trouvé: {user.id}")

        logger.debug(f"Utilisateur mis à jour: {user.username}")
        return user

    async def delete_user(self, user_id: str) -> bool:
        """Supprime un utilisateur par son ID (ObjectId string)."""
        try:
            result = await self._collection.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count > 0:
                logger.debug(f"Utilisateur supprimé: {user_id}")
                return True
        except Exception:
            pass
        return False

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[AuthUser]:
        """Liste les utilisateurs avec pagination."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active

        cursor = self._collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)

        return [self._mapper.to_entity(doc) for doc in docs]

    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """Compte le nombre d'utilisateurs."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active

        return await self._collection.count_documents(query)

    async def username_exists(self, username: str) -> bool:
        """Vérifie si un username existe."""
        count = await self._collection.count_documents({"username": username})
        return count > 0

    async def email_exists(self, email: str) -> bool:
        """Vérifie si un email existe."""
        count = await self._collection.count_documents({"email": email})
        return count > 0

    async def find_by_extra_field(
        self,
        field_name: str,
        value: Any,
    ) -> Optional[AuthUser]:
        """
        Recherche un utilisateur par un champ personnalisé.

        Args:
            field_name: Nom du champ personnalisé
            value: Valeur à rechercher

        Returns:
            Utilisateur trouvé ou None
        """
        doc = await self._collection.find_one({field_name: value})
        if doc:
            return self._mapper.to_entity(doc)
        return None

    async def list_by_extra_field(
        self,
        field_name: str,
        value: Any,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuthUser]:
        """
        Liste les utilisateurs par un champ personnalisé.

        Args:
            field_name: Nom du champ personnalisé
            value: Valeur à rechercher
            skip: Offset pour la pagination
            limit: Limite du nombre de résultats

        Returns:
            Liste d'utilisateurs correspondants
        """
        cursor = (
            self._collection
            .find({field_name: value})
            .skip(skip)
            .limit(limit)
            .sort("created_at", -1)
        )
        docs = await cursor.to_list(length=limit)

        return [self._mapper.to_entity(doc) for doc in docs]

    async def create_indexes(self, extra_indexes: Optional[List[str]] = None) -> None:
        """
        Crée les index nécessaires pour optimiser les requêtes.

        Args:
            extra_indexes: Liste de noms de champs personnalisés à indexer

        À appeler lors de l'initialisation.
        """
        # Index composites uniques : username et email uniques par tenant
        await self._collection.create_index(
            [("tenant_id", 1), ("username", 1)],
            unique=True,
            name="uq_user_tenant_username"
        )
        await self._collection.create_index(
            [("tenant_id", 1), ("email", 1)],
            unique=True,
            name="uq_user_tenant_email"
        )
        # Index simples pour les recherches
        # await self._collection.create_index("username")
        # await self._collection.create_index("email")
        # await self._collection.create_index("tenant_id")
        await self._collection.create_index("is_active")
        await self._collection.create_index("created_at")

        # Index sur les champs personnalisés
        if extra_indexes:
            for field_name in extra_indexes:
                await self._collection.create_index(field_name)
                logger.debug(f"Index créé pour le champ personnalisé: {field_name}")

        logger.info(f"Index MongoDB créés pour {self._collection_name}")

    async def update_extra_field(
        self,
        user_id: str,
        field_name: str,
        value: Any,
    ) -> bool:
        """
        Met à jour un seul champ personnalisé.

        Args:
            user_id: ID de l'utilisateur
            field_name: Nom du champ à mettre à jour
            value: Nouvelle valeur

        Returns:
            True si la mise à jour a réussi
        """
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {field_name: value}}
        )
        return result.modified_count > 0

    async def add_to_array_field(
        self,
        user_id: str,
        field_name: str,
        value: Any,
    ) -> bool:
        """
        Ajoute une valeur à un champ de type array.

        Args:
            user_id: ID de l'utilisateur
            field_name: Nom du champ array
            value: Valeur à ajouter

        Returns:
            True si l'ajout a réussi
        """
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {field_name: value}}
        )
        return result.modified_count > 0

    async def remove_from_array_field(
        self,
        user_id: str,
        field_name: str,
        value: Any,
    ) -> bool:
        """
        Retire une valeur d'un champ de type array.

        Args:
            user_id: ID de l'utilisateur
            field_name: Nom du champ array
            value: Valeur à retirer

        Returns:
            True si la suppression a réussi
        """
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {field_name: value}}
        )
        return result.modified_count > 0
