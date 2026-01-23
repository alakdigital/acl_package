"""
Repository MongoDB pour les rôles.
"""

from typing import Any, Optional, List, Type
from datetime import datetime

from bson import ObjectId

from ...application.interface.role_repository import IRoleRepository
from ...domain.entities.role import Role
from ..models.mongo_model import MongoRoleModel
from ..mappers.role_mapper import RoleMapper
from ....shared.database.mongodb import MongoDBDatabase
from ....shared.exceptions import RoleAlreadyExistsError, RoleNotFoundError, PermissionDeniedError
from ....shared.logging import logger


class MongoDBRoleRepository(IRoleRepository):
    """
    Implémentation du repository des rôles pour MongoDB.

    Utilise motor pour les opérations asynchrones.
    """

    def __init__(
        self,
        db: MongoDBDatabase,
        roles_collection: str = "acl_roles",
        user_roles_collection: str = "acl_user_roles",
        model_class: Type[MongoRoleModel] = MongoRoleModel,
        mapper: Optional[RoleMapper] = None,
    ):
        """
        Initialise le repository.

        Args:
            db: Instance de MongoDBDatabase
            roles_collection: Nom de la collection des rôles
            user_roles_collection: Nom de la collection des associations
            model_class: Classe du modèle rôle
            mapper: Instance du mapper
        """
        self._db = db
        self._roles_collection_name = roles_collection
        self._user_roles_collection_name = user_roles_collection
        self._model_class = model_class
        self._mapper = mapper or RoleMapper(mongo_model_class=model_class)

    @property
    def _roles_collection(self):
        """Retourne la collection des rôles."""
        return self._db.get_collection(self._roles_collection_name)

    @property
    def _user_roles_collection(self):
        """Retourne la collection des associations user-role."""
        return self._db.get_collection(self._user_roles_collection_name)

    @property
    def model_class(self) -> Type[MongoRoleModel]:
        """Retourne la classe du modèle utilisé."""
        return self._model_class

    # ==========================================
    # CRUD Rôles
    # ==========================================

    async def create_role(self, role: Role) -> Role:
        """Crée un nouveau rôle."""
        # Vérifier l'unicité du nom
        existing = await self._roles_collection.find_one({"name": role.name})
        if existing:
            raise RoleAlreadyExistsError(f"Un rôle avec le nom '{role.name}' existe déjà")

        doc = self._mapper.to_mongo_dict(role)
        doc.pop("_id", None)

        result = await self._roles_collection.insert_one(doc)
        role.id = str(result.inserted_id)

        logger.debug(f"Rôle créé: {role.name} (id: {role.id})")
        return role

    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """Récupère un rôle par son ID."""
        try:
            doc = await self._roles_collection.find_one({"_id": ObjectId(role_id)})
            if doc:
                return self._mapper.to_entity(doc)
        except Exception:
            pass
        return None

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Récupère un rôle par son nom."""
        doc = await self._roles_collection.find_one({"name": name})
        if doc:
            return self._mapper.to_entity(doc)
        return None

    async def update_role(self, role: Role) -> Role:
        """Met à jour un rôle."""
        doc = self._mapper.to_mongo_dict(role)
        doc["updated_at"] = datetime.utcnow()

        result = await self._roles_collection.update_one(
            {"_id": ObjectId(role.id)},
            {"$set": doc}
        )

        if result.matched_count == 0:
            raise RoleNotFoundError(f"Rôle non trouvé: {role.id}")

        logger.debug(f"Rôle mis à jour: {role.name}")
        return role

    async def delete_role(self, role_id: str) -> bool:
        """Supprime un rôle."""
        try:
            # Vérifier si c'est un rôle système
            doc = await self._roles_collection.find_one({"_id": ObjectId(role_id)})
            if doc and doc.get("is_system"):
                raise PermissionDeniedError("Impossible de supprimer un rôle système")

            # Supprimer les associations
            await self._user_roles_collection.delete_many({"role_id": role_id})

            # Supprimer le rôle
            result = await self._roles_collection.delete_one({"_id": ObjectId(role_id)})

            if result.deleted_count > 0:
                logger.debug(f"Rôle supprimé: {role_id}")
                return True
        except PermissionDeniedError:
            raise
        except Exception:
            pass
        return False

    async def list_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Role]:
        """Liste les rôles avec pagination."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active

        cursor = (
            self._roles_collection
            .find(query)
            .skip(skip)
            .limit(limit)
            .sort([("priority", -1), ("name", 1)])
        )
        docs = await cursor.to_list(length=limit)

        return [self._mapper.to_entity(doc) for doc in docs]

    async def count_roles(self, is_active: Optional[bool] = None) -> int:
        """Compte le nombre de rôles."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active

        return await self._roles_collection.count_documents(query)

    async def role_exists(self, name: str) -> bool:
        """Vérifie si un rôle existe."""
        count = await self._roles_collection.count_documents({"name": name})
        return count > 0

    async def get_default_roles(self) -> List[Role]:
        """Récupère tous les rôles par défaut."""
        cursor = self._roles_collection.find({
            "is_default": True,
            "is_active": True,
        })
        docs = await cursor.to_list(length=100)
        return [self._mapper.to_entity(doc) for doc in docs]

    # ==========================================
    # Assignation des rôles
    # ==========================================

    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assigne un rôle à un utilisateur."""
        # Vérifier que le rôle existe
        role_exists = await self._roles_collection.find_one({"_id": ObjectId(role_id)})
        if not role_exists:
            raise RoleNotFoundError(f"Rôle non trouvé: {role_id}")

        # Vérifier si l'association existe déjà
        existing = await self._user_roles_collection.find_one({
            "user_id": user_id,
            "role_id": role_id,
        })
        if existing:
            return True  # Déjà assigné

        # Créer l'association
        await self._user_roles_collection.insert_one({
            "user_id": user_id,
            "role_id": role_id,
            "assigned_at": datetime.utcnow(),
        })

        logger.debug(f"Rôle {role_id} assigné à l'utilisateur {user_id}")
        return True

    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Retire un rôle d'un utilisateur."""
        result = await self._user_roles_collection.delete_one({
            "user_id": user_id,
            "role_id": role_id,
        })
        deleted = result.deleted_count > 0

        if deleted:
            logger.debug(f"Rôle {role_id} retiré de l'utilisateur {user_id}")

        return deleted

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Récupère tous les rôles d'un utilisateur."""
        # Récupérer les IDs des rôles
        cursor = self._user_roles_collection.find({"user_id": user_id})
        user_roles = await cursor.to_list(length=100)
        role_ids = [ObjectId(ur["role_id"]) for ur in user_roles]

        if not role_ids:
            return []

        # Récupérer les rôles
        cursor = (
            self._roles_collection
            .find({"_id": {"$in": role_ids}})
            .sort("priority", -1)
        )
        docs = await cursor.to_list(length=100)

        return [self._mapper.to_entity(doc) for doc in docs]

    async def get_users_with_role(
        self,
        role_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """Récupère les IDs des utilisateurs ayant un rôle."""
        cursor = (
            self._user_roles_collection
            .find({"role_id": role_id})
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [doc["user_id"] for doc in docs]

    async def user_has_role(self, user_id: str, role_id: str) -> bool:
        """Vérifie si un utilisateur a un rôle."""
        count = await self._user_roles_collection.count_documents({
            "user_id": user_id,
            "role_id": role_id,
        })
        return count > 0

    async def user_has_role_by_name(self, user_id: str, role_name: str) -> bool:
        """Vérifie si un utilisateur a un rôle par son nom."""
        # Trouver le rôle
        role = await self._roles_collection.find_one({"name": role_name})
        if not role:
            return False

        # Vérifier l'association
        return await self.user_has_role(user_id, str(role["_id"]))

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Récupère toutes les permissions d'un utilisateur."""
        roles = await self.get_user_roles(user_id)
        permissions = set()
        for role in roles:
            if role.is_active:
                permissions.update(role.permissions)
        return sorted(list(permissions))

    async def set_user_roles(self, user_id: str, role_ids: List[str]) -> bool:
        """Définit la liste complète des rôles d'un utilisateur."""
        # Supprimer tous les rôles existants
        await self._user_roles_collection.delete_many({"user_id": user_id})

        # Ajouter les nouveaux rôles
        if role_ids:
            docs = [
                {
                    "user_id": user_id,
                    "role_id": role_id,
                    "assigned_at": datetime.utcnow(),
                }
                for role_id in role_ids
            ]
            await self._user_roles_collection.insert_many(docs)

        logger.debug(f"Rôles mis à jour pour l'utilisateur {user_id}: {role_ids}")
        return True

    async def clear_user_roles(self, user_id: str) -> bool:
        """Supprime tous les rôles d'un utilisateur."""
        await self._user_roles_collection.delete_many({"user_id": user_id})
        logger.debug(f"Rôles supprimés pour l'utilisateur {user_id}")
        return True

    # ==========================================
    # Index MongoDB
    # ==========================================

    async def create_indexes(self) -> None:
        """Crée les index nécessaires."""
        # Index sur les rôles
        await self._roles_collection.create_index("name", unique=True)
        await self._roles_collection.create_index("is_active")
        await self._roles_collection.create_index("is_default")
        await self._roles_collection.create_index("priority")

        # Index sur les associations user-role
        await self._user_roles_collection.create_index(
            [("user_id", 1), ("role_id", 1)],
            unique=True
        )
        await self._user_roles_collection.create_index("user_id")
        await self._user_roles_collection.create_index("role_id")

        logger.info(f"Index MongoDB créés pour les rôles")
