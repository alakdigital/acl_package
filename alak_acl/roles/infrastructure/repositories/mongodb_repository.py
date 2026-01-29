"""
Repository MongoDB pour les rôles.
"""

from typing import Any, Optional, List, Type
from datetime import datetime

from bson import ObjectId

from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.roles.domain.entities.role import Role
from alak_acl.roles.infrastructure.mappers.role_mapper import RoleMapper
from alak_acl.roles.infrastructure.models.mongo_model import MongoRoleModel
from alak_acl.shared.database.mongodb import MongoDBDatabase
from alak_acl.shared.exceptions import PermissionDeniedError, RoleAlreadyExistsError, RoleInUseError, RoleNotFoundError
from alak_acl.shared.logging import logger


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
            raise RoleAlreadyExistsError("name",f"Un rôle avec le nom '{role.name}' existe déjà")

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
            raise RoleNotFoundError("id", f"Rôle non trouvé: {role.id}")

        logger.debug(f"Rôle mis à jour: {role.name}")
        return role

    async def delete_role(self, role_id: str) -> bool:
        """
        Supprime un rôle.

        Conditions de suppression:
        - Le rôle ne doit pas être un rôle système
        - Le rôle ne doit pas être assigné à des utilisateurs
        - Le rôle ne doit pas avoir de permissions associées

        Raises:
            PermissionDeniedError: Si c'est un rôle système
            RoleInUseError: Si le rôle est assigné à des utilisateurs ou a des permissions
        """
        try:
            # Vérifier si le rôle existe et récupérer ses données
            doc = await self._roles_collection.find_one({"_id": ObjectId(role_id)})
            if not doc:
                return False

            # Vérifier si c'est un rôle système
            if doc.get("is_system"):
                raise PermissionDeniedError("Impossible de supprimer un rôle système")

            # Vérifier si le rôle est assigné à des utilisateurs
            user_count = await self._user_roles_collection.count_documents({"role_id": role_id})
            if user_count > 0:
                raise RoleInUseError(
                    f"Impossible de supprimer le rôle: il est assigné à {user_count} utilisateur(s)"
                )

            # Vérifier si le rôle a des permissions
            permissions = doc.get("permissions", [])
            if permissions and len(permissions) > 0:
                raise RoleInUseError(
                    f"Impossible de supprimer le rôle: il possède {len(permissions)} permission(s)"
                )

            # Supprimer le rôle
            result = await self._roles_collection.delete_one({"_id": ObjectId(role_id)})

            if result.deleted_count > 0:
                logger.debug(f"Rôle supprimé: {role_id}")
                return True
        except (PermissionDeniedError, RoleInUseError):
            raise
        except Exception:
            pass
        return False

    async def list_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Role]:
        """Liste les rôles avec pagination."""
        query: dict[str, Any] = {}
        if is_active is not None:
            query["is_active"] = is_active
        if tenant_id is not None:
            query["tenant_id"] = tenant_id

        cursor = (
            self._roles_collection
            .find(query)
            .skip(skip)
            .limit(limit)
            .sort([("priority", -1), ("name", 1)])
        )
        docs = await cursor.to_list(length=limit)

        return [self._mapper.to_entity(doc) for doc in docs]

    async def count_roles(
        self,
        is_active: Optional[bool] = None,
        tenant_id: Optional[str] = None,
    ) -> int:
        """Compte le nombre de rôles."""
        query: dict[str, Any] = {}
        if is_active is not None:
            query["is_active"] = is_active
        if tenant_id is not None:
            query["tenant_id"] = tenant_id

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

    async def get_default_role(self) -> Optional[Role]:
        """Récupère le rôle par défaut."""
        doc = await self._roles_collection.find_one({
            "is_default": True,
            "is_active": True,
        })
        if doc:
            return self._mapper.to_entity(doc)
        return None

    async def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        tenant_id: Optional[str] = None,
        assigned_by: Optional[str] = None,
    ) -> bool:
        """Assigne un rôle à un utilisateur (avec ou sans tenant)."""
        # Vérifier que le rôle existe
        role_exists = await self._roles_collection.find_one({"_id": ObjectId(role_id)})
        if not role_exists:
            raise RoleNotFoundError("id", f"Rôle non trouvé: {role_id}")

        # Vérifier si l'association existe déjà
        query: dict[str, Any] = {
            "user_id": user_id,
            "role_id": role_id,
            "tenant_id": tenant_id,
        }
        existing = await self._user_roles_collection.find_one(query)
        if existing:
            return True  # Déjà assigné

        # Créer l'association
        doc: dict[str, Any] = {
            "user_id": user_id,
            "role_id": role_id,
            "tenant_id": tenant_id,
            "assigned_at": datetime.utcnow(),
        }
        if assigned_by:
            doc["assigned_by"] = assigned_by

        await self._user_roles_collection.insert_one(doc)

        logger.debug(f"Rôle {role_id} assigné à user {user_id}" + (f" dans tenant {tenant_id}" if tenant_id else ""))
        return True

    async def remove_role_from_user(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
    ) -> bool:
        """Retire un rôle d'un utilisateur dans un tenant."""
        result = await self._user_roles_collection.delete_one({
            "user_id": user_id,
            "role_id": role_id,
            "tenant_id": tenant_id,
        })
        deleted = result.deleted_count > 0

        if deleted:
            logger.debug(f"Rôle {role_id} retiré de user {user_id} dans tenant {tenant_id}")

        return deleted

    async def get_user_roles(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
    ) -> List[Role]:
        """
        Récupère les rôles d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            tenant_id: ID du tenant. Si None, retourne les rôles globaux (tenant_id=null).

        Returns:
            Liste des rôles de l'utilisateur pour le tenant spécifié
        """
        # Construire la requête - toujours filtrer par tenant_id (y compris null)
        query: dict[str, Any] = {"user_id": user_id, "tenant_id": tenant_id}

        # Récupérer les IDs des rôles
        cursor = self._user_roles_collection.find(query)
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

    async def get_user_tenants(self, user_id: str) -> List[str]:
        """Récupère les IDs des tenants auxquels un utilisateur appartient."""
        cursor = self._user_roles_collection.find(
            {"user_id": user_id},
            {"tenant_id": 1}
        )
        docs = await cursor.to_list(length=1000)
        # Retourner les tenant_id uniques non nuls
        tenants = set()
        for doc in docs:
            if doc.get("tenant_id"):
                tenants.add(doc["tenant_id"])
        return list(tenants)

    async def get_users_with_role(
        self,
        role_id: str,
        tenant_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """Récupère les IDs des utilisateurs ayant un rôle."""
        query: dict[str, Any] = {"role_id": role_id}
        if tenant_id is not None:
            query["tenant_id"] = tenant_id

        cursor = (
            self._user_roles_collection
            .find(query)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        # Retourner les user_id uniques
        return list(set(doc["user_id"] for doc in docs))

    async def user_has_role(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
    ) -> bool:
        """Vérifie si un utilisateur a un rôle dans un tenant."""
        count = await self._user_roles_collection.count_documents({
            "user_id": user_id,
            "role_id": role_id,
            "tenant_id": tenant_id,
        })
        return count > 0

    async def user_has_role_by_name(
        self,
        user_id: str,
        role_name: str,
        tenant_id: str,
    ) -> bool:
        """Vérifie si un utilisateur a un rôle par son nom dans un tenant."""
        # Trouver le rôle
        role = await self._roles_collection.find_one({"name": role_name})
        if not role:
            return False

        # Vérifier l'association
        return await self.user_has_role(user_id, str(role["_id"]), tenant_id)

    async def get_user_permissions(
        self,
        user_id: str,
        tenant_id: str,
    ) -> List[str]:
        """Récupère toutes les permissions d'un utilisateur dans un tenant."""
        roles = await self.get_user_roles(user_id, tenant_id)
        permissions = set()
        for role in roles:
            if role.is_active:
                permissions.update(role.permissions)
        return sorted(list(permissions))

    async def set_user_roles(
        self,
        user_id: str,
        role_ids: List[str],
        tenant_id: str,
    ) -> bool:
        """Définit la liste complète des rôles d'un utilisateur dans un tenant."""
        # Supprimer les rôles existants pour ce tenant
        await self._user_roles_collection.delete_many({
            "user_id": user_id,
            "tenant_id": tenant_id,
        })

        # Ajouter les nouveaux rôles
        if role_ids:
            docs = [
                {
                    "user_id": user_id,
                    "role_id": role_id,
                    "tenant_id": tenant_id,
                    "assigned_at": datetime.utcnow(),
                }
                for role_id in role_ids
            ]
            await self._user_roles_collection.insert_many(docs)

        logger.debug(f"Rôles mis à jour pour user {user_id} dans tenant {tenant_id}: {role_ids}")
        return True

    async def clear_user_roles(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Supprime les rôles d'un utilisateur."""
        query: dict[str, Any] = {"user_id": user_id}
        if tenant_id is not None:
            query["tenant_id"] = tenant_id

        await self._user_roles_collection.delete_many(query)
        logger.debug(f"Rôles supprimés pour user {user_id}" + (f" dans tenant {tenant_id}" if tenant_id else ""))
        return True

    async def get_tenant_members(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """Récupère les IDs des utilisateurs membres d'un tenant."""
        cursor = (
            self._user_roles_collection
            .find({"tenant_id": tenant_id})
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        # Retourner les user_id uniques
        return list(set(doc["user_id"] for doc in docs))

    async def count_tenant_members(self, tenant_id: str) -> int:
        """Compte le nombre de membres d'un tenant."""
        # Utiliser une agrégation pour compter les utilisateurs distincts
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {"_id": "$user_id"}},
            {"$count": "total"}
        ]
        result = await self._user_roles_collection.aggregate(pipeline).to_list(length=1)
        if result:
            return result[0].get("total", 0)
        return 0

    # ==========================================
    # Vérifications pour la suppression
    # ==========================================

    async def count_roles_with_permission(self, permission_name: str) -> int:
        """Compte le nombre de rôles qui utilisent une permission."""
        return await self._roles_collection.count_documents({
            "permissions": permission_name
        })

    # ==========================================
    # Index MongoDB
    # ==========================================

    async def create_indexes(self) -> None:
        """Crée les index nécessaires."""
        # Index composite unique : nom unique par tenant
        await self._roles_collection.create_index(
            [("tenant_id", 1), ("name", 1)],
            unique=True,
            name="uq_role_tenant_name"
        )
        # Index simple sur name pour les recherches
        # await self._roles_collection.create_index("name")
        # await self._roles_collection.create_index("tenant_id")
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
