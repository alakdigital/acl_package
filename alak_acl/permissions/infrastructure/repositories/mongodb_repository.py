"""
Repository MongoDB pour les permissions.

Implémentation asynchrone utilisant Motor.
"""

from datetime import datetime
from typing import List, Optional
import re

from bson import ObjectId

from alak_acl.permissions.application.interface.permission_repository import IPermissionRepository
from alak_acl.permissions.domain.entities.permission import Permission
from alak_acl.permissions.infrastructure.mappers.permission_mapper import PermissionMapper
from alak_acl.shared.database.mongodb import MongoDBDatabase
from alak_acl.shared.exceptions import PermissionAlreadyExistsError, PermissionNotFoundError


from alak_acl.shared.logging import logger


class MongoDBPermissionRepository(IPermissionRepository):
    """
    Implémentation du repository des permissions pour MongoDB.

    Utilise Motor pour les opérations asynchrones.
    """

    def __init__(
        self,
        db: MongoDBDatabase,
        collection_name: str = "acl_permissions",
    ):
        """
        Initialise le repository.

        Args:
            db: Instance de MongoDBDatabase
            collection_name: Nom de la collection
        """
        self._db = db
        self._collection_name = collection_name
        self._mapper = PermissionMapper()

    @property
    def _collection(self):
        """Retourne la collection MongoDB."""
        return self._db.get_collection(self._collection_name)

    async def create_indexes(self) -> None:
        """
        Crée les index nécessaires pour optimiser les requêtes.

        À appeler lors de l'initialisation.
        """
        await self._collection.create_index("name", unique=True)
        await self._collection.create_index("resource")
        await self._collection.create_index("action")
        await self._collection.create_index("category")
        await self._collection.create_index("is_active")
        await self._collection.create_index(
            [("resource", 1), ("action", 1)]
        )
        logger.info(f"Index MongoDB créés pour {self._collection_name}")

    # ============================================
    # CRUD Operations
    # ============================================

    async def create_permission(self, permission: Permission) -> Permission:
        """Crée une nouvelle permission."""
        # Vérifier l'unicité
        existing = await self._collection.find_one({"name": permission.name})
        if existing:
            raise PermissionAlreadyExistsError(
                "name",
                f"Permission '{permission.name}' existe déjà"
            )

        doc = self._mapper.to_mongo_dict(permission)
        result = await self._collection.insert_one(doc)
        permission.id = str(result.inserted_id)

        logger.debug(f"Permission créée: {permission.name}")
        return permission

    async def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """Récupère une permission par son ID."""
        try:
            doc = await self._collection.find_one({"_id": ObjectId(permission_id)})
            if doc:
                return self._mapper.to_entity(doc)
        except Exception:
            pass
        return None

    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Récupère une permission par son nom (resource:action)."""
        doc = await self._collection.find_one({"name": name.lower()})
        if doc:
            return self._mapper.to_entity(doc)
        return None

    async def update_permission(self, permission: Permission) -> Permission:
        """Met à jour une permission existante."""
        result = await self._collection.update_one(
            {"_id": ObjectId(permission.id)},
            {
                "$set": {
                    "display_name": permission.display_name,
                    "description": permission.description,
                    "category": permission.category,
                    "is_active": permission.is_active,
                    "updated_at": datetime.utcnow(),
                }
            }
        )

        if result.matched_count == 0:
            raise PermissionNotFoundError(
                "id",
                f"Permission non trouvée: {permission.id}"
            )

        logger.debug(f"Permission mise à jour: {permission.name}")
        return permission

    async def delete_permission(self, permission_id: str) -> bool:
        """Supprime une permission."""
        try:
            # Vérifier si c'est une permission système
            doc = await self._collection.find_one({"_id": ObjectId(permission_id)})
            if doc and doc.get("is_system"):
                raise PermissionNotFoundError(
                    "id",
                    "Impossible de supprimer une permission système"
                )

            result = await self._collection.delete_one(
                {"_id": ObjectId(permission_id)}
            )
            if result.deleted_count > 0:
                logger.debug(f"Permission supprimée: {permission_id}")
                return True
        except Exception as e:
            if "système" in str(e):
                raise
        return False

    # ============================================
    # Query Operations
    # ============================================

    async def list_permissions(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> List[Permission]:
        """Liste les permissions avec pagination et filtres."""
        query = {}

        if is_active is not None:
            query["is_active"] = is_active
        if category:
            query["category"] = category
        if resource:
            query["resource"] = resource.lower()

        cursor = (
            self._collection
            .find(query)
            .sort([("category", 1), ("resource", 1), ("action", 1)])
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)

        return [self._mapper.to_entity(doc) for doc in docs]

    async def count_permissions(
        self,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> int:
        """Compte le nombre de permissions."""
        query = {}

        if is_active is not None:
            query["is_active"] = is_active
        if category:
            query["category"] = category
        if resource:
            query["resource"] = resource.lower()

        return await self._collection.count_documents(query)

    async def get_by_resource(self, resource: str) -> List[Permission]:
        """Récupère toutes les permissions d'une ressource."""
        cursor = (
            self._collection
            .find({"resource": resource.lower(), "is_active": True})
            .sort("action", 1)
        )
        docs = await cursor.to_list(length=1000)
        return [self._mapper.to_entity(doc) for doc in docs]

    async def get_by_category(self, category: str) -> List[Permission]:
        """Récupère toutes les permissions d'une catégorie."""
        cursor = (
            self._collection
            .find({"category": category, "is_active": True})
            .sort([("resource", 1), ("action", 1)])
        )
        docs = await cursor.to_list(length=1000)
        return [self._mapper.to_entity(doc) for doc in docs]

    async def get_all_resources(self) -> List[str]:
        """Récupère la liste de toutes les ressources distinctes."""
        resources = await self._collection.distinct("resource")
        return sorted(resources)

    async def get_all_categories(self) -> List[str]:
        """Récupère la liste de toutes les catégories distinctes."""
        categories = await self._collection.distinct("category")
        return sorted([c for c in categories if c])

    # ============================================
    # Bulk Operations
    # ============================================

    async def create_many(self, permissions: List[Permission]) -> List[Permission]:
        """Crée plusieurs permissions en une seule opération."""
        created = []

        for permission in permissions:
            existing = await self._collection.find_one({"name": permission.name})
            if existing:
                logger.debug(f"Permission existe déjà: {permission.name}")
                continue

            doc = self._mapper.to_mongo_dict(permission)
            result = await self._collection.insert_one(doc)
            permission.id = str(result.inserted_id)
            created.append(permission)

        logger.info(f"{len(created)} permissions créées")
        return created

    async def get_by_ids(self, permission_ids: List[str]) -> List[Permission]:
        """Récupère plusieurs permissions par leurs IDs."""
        if not permission_ids:
            return []

        try:
            object_ids = [ObjectId(pid) for pid in permission_ids]
            cursor = self._collection.find({"_id": {"$in": object_ids}})
            docs = await cursor.to_list(length=len(permission_ids))
            return [self._mapper.to_entity(doc) for doc in docs]
        except Exception:
            return []

    async def get_by_names(self, names: List[str]) -> List[Permission]:
        """Récupère plusieurs permissions par leurs noms."""
        if not names:
            return []

        normalized_names = [n.lower() for n in names]
        cursor = self._collection.find({"name": {"$in": normalized_names}})
        docs = await cursor.to_list(length=len(names))
        return [self._mapper.to_entity(doc) for doc in docs]

    # ============================================
    # Utility Methods
    # ============================================

    async def permission_exists(self, name: str) -> bool:
        """Vérifie si une permission existe par son nom."""
        count = await self._collection.count_documents({"name": name.lower()})
        return count > 0

    async def search_permissions(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Permission]:
        """Recherche des permissions par texte."""
        search_regex = re.compile(re.escape(query), re.IGNORECASE)
        cursor = (
            self._collection
            .find({
                "$or": [
                    {"name": search_regex},
                    {"display_name": search_regex},
                    {"description": search_regex},
                ]
            })
            .sort("name", 1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._mapper.to_entity(doc) for doc in docs]
