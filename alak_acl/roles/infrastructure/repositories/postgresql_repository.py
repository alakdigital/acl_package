"""
Repository PostgreSQL pour les rôles et memberships.
"""

from typing import Optional, List, Type

from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError


from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.roles.domain.entities.role import Role
from alak_acl.roles.infrastructure.mappers.role_mapper import RoleMapper
from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel, SQLMembershipModel
from alak_acl.shared.database.postgresql import PostgreSQLDatabase
from alak_acl.shared.exceptions import PermissionDeniedError, RoleAlreadyExistsError, RoleInUseError, RoleNotFoundError
from alak_acl.shared.logging import logger


class PostgreSQLRoleRepository(IRoleRepository):
    """
    Implémentation du repository des rôles pour PostgreSQL.

    Utilise SQLAlchemy 2.0 async.
    """

    def __init__(
        self,
        db: PostgreSQLDatabase,
        model_class: Type[SQLRoleModel] = SQLRoleModel,
        mapper: Optional[RoleMapper] = None,
    ):
        """
        Initialise le repository.

        Args:
            db: Instance de PostgreSQLDatabase
            model_class: Classe du modèle rôle
            mapper: Instance du mapper
        """
        self._db = db
        self._model_class = model_class
        self._mapper = mapper or RoleMapper(sql_model_class=model_class)

    @property
    def model_class(self) -> Type[SQLRoleModel]:
        """Retourne la classe du modèle utilisé."""
        return self._model_class

    # ==========================================
    # CRUD Rôles
    # ==========================================

    async def create_role(self, role: Role) -> Role:
        """Crée un nouveau rôle."""
        model = self._mapper.to_sql_model(role, self._model_class)

        async with self._db.session() as session:
            try:
                session.add(model)
                await session.flush()
                await session.refresh(model)
                logger.debug(f"Rôle créé: {role.name}")
                return self._mapper.to_entity(model)
            except IntegrityError as e:
                logger.warning(f"Erreur d'intégrité lors de la création du rôle: {e}")
                raise RoleAlreadyExistsError("name",f"Un rôle avec le nom '{role.name}' existe déjà")

    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """Récupère un rôle par son ID."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.id == role_id)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._mapper.to_entity(model)
            return None

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Récupère un rôle par son nom."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.name == name)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._mapper.to_entity(model)
            return None

    async def update_role(self, role: Role) -> Role:
        """Met à jour un rôle."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.id == role.id)
            )
            model = result.scalar_one_or_none()

            if not model:
                raise RoleNotFoundError("id", f"Rôle non trouvé: {role.id}")

            self._mapper.update_sql_model(model, role)
            await session.flush()
            await session.refresh(model)

            logger.debug(f"Rôle mis à jour: {role.name}")
            return self._mapper.to_entity(model)

    async def delete_role(self, role_id: str) -> bool:
        """
        Supprime un rôle.

        Conditions de suppression:
        - Le rôle ne doit pas être un rôle système
        - Le rôle ne doit pas être assigné à des utilisateurs (via memberships)
        - Le rôle ne doit pas avoir de permissions associées

        Raises:
            PermissionDeniedError: Si c'est un rôle système
            RoleInUseError: Si le rôle est utilisé
        """
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.id == role_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return False

            if model.is_system:
                raise PermissionDeniedError("Impossible de supprimer un rôle système")

            # Vérifier si le rôle est utilisé dans des memberships
            membership_count_result = await session.execute(
                select(func.count(SQLMembershipModel.id)).where(
                    SQLMembershipModel.role_id == role_id
                )
            )
            membership_count = membership_count_result.scalar_one()
            if membership_count > 0:
                raise RoleInUseError(
                    f"Impossible de supprimer le rôle: il est assigné à {membership_count} membership(s)"
                )

            # Vérifier si le rôle a des permissions
            if model.permissions and len(model.permissions) > 0:
                raise RoleInUseError(
                    f"Impossible de supprimer le rôle: il possède {len(model.permissions)} permission(s)"
                )

            await session.delete(model)
            logger.debug(f"Rôle supprimé: {role_id}")
            return True

    async def list_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Role]:
        """Liste les rôles avec pagination."""
        async with self._db.session() as session:
            query = select(self._model_class)

            if is_active is not None:
                query = query.where(self._model_class.is_active == is_active)

            if tenant_id is not None:
                query = query.where(self._model_class.tenant_id == tenant_id)

            query = query.offset(skip).limit(limit).order_by(
                self._model_class.priority.desc(),
                self._model_class.name.asc()
            )

            result = await session.execute(query)
            models = result.scalars().all()

            return [self._mapper.to_entity(model) for model in models]

    async def count_roles(
        self,
        is_active: Optional[bool] = None,
        tenant_id: Optional[str] = None,
    ) -> int:
        """Compte le nombre de rôles."""
        async with self._db.session() as session:
            query = select(func.count(self._model_class.id))

            if is_active is not None:
                query = query.where(self._model_class.is_active == is_active)

            if tenant_id is not None:
                query = query.where(self._model_class.tenant_id == tenant_id)

            result = await session.execute(query)
            return result.scalar_one()

    async def role_exists(self, name: str) -> bool:
        """Vérifie si un rôle existe."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(self._model_class.id)).where(
                    self._model_class.name == name
                )
            )
            return result.scalar_one() > 0

    async def get_default_roles(self) -> List[Role]:
        """Récupère tous les rôles par défaut."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(
                    self._model_class.is_default == True,
                    self._model_class.is_active == True,
                )
            )
            models = result.scalars().all()
            return [self._mapper.to_entity(model) for model in models]

    async def get_default_role(self) -> Optional[Role]:
        """Récupère le rôle par défaut."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(
                    self._model_class.is_default == True,
                    self._model_class.is_active == True,
                ).limit(1)
            )
            model = result.scalar_one_or_none()
            if model:
                return self._mapper.to_entity(model)
            return None

    # ==========================================
    # Memberships (user <-> tenant <-> role)
    # ==========================================

    async def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
        assigned_by: Optional[str] = None,
    ) -> bool:
        """Assigne un rôle à un utilisateur dans un tenant."""
        async with self._db.session() as session:
            # Vérifier que le rôle existe
            role_result = await session.execute(
                select(self._model_class).where(self._model_class.id == role_id)
            )
            if not role_result.scalar_one_or_none():
                raise RoleNotFoundError("id", f"Rôle non trouvé: {role_id}")

            # Vérifier si le membership existe déjà
            existing = await session.execute(
                select(SQLMembershipModel).where(
                    SQLMembershipModel.user_id == user_id,
                    SQLMembershipModel.tenant_id == tenant_id,
                    SQLMembershipModel.role_id == role_id,
                )
            )
            if existing.scalar_one_or_none():
                return True  # Déjà assigné

            # Créer le membership
            membership = SQLMembershipModel(
                user_id=user_id,
                tenant_id=tenant_id,
                role_id=role_id,
                assigned_by=assigned_by,
            )
            session.add(membership)
            await session.flush()

            logger.debug(f"Rôle {role_id} assigné à user {user_id} dans tenant {tenant_id}")
            return True

    async def remove_role_from_user(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
    ) -> bool:
        """Retire un rôle d'un utilisateur dans un tenant."""
        async with self._db.session() as session:
            result = await session.execute(
                delete(SQLMembershipModel).where(
                    SQLMembershipModel.user_id == user_id,
                    SQLMembershipModel.tenant_id == tenant_id,
                    SQLMembershipModel.role_id == role_id,
                )
            )
            deleted = result.rowcount > 0

            if deleted:
                logger.debug(f"Rôle {role_id} retiré de user {user_id} dans tenant {tenant_id}")

            return deleted

    async def get_user_roles(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
    ) -> List[Role]:
        """Récupère les rôles d'un utilisateur."""
        async with self._db.session() as session:
            query = (
                select(self._model_class)
                .join(SQLMembershipModel, SQLMembershipModel.role_id == self._model_class.id)
                .where(SQLMembershipModel.user_id == user_id)
            )

            if tenant_id is not None:
                query = query.where(SQLMembershipModel.tenant_id == tenant_id)

            query = query.order_by(self._model_class.priority.desc())

            result = await session.execute(query)
            models = result.scalars().all()
            return [self._mapper.to_entity(model) for model in models]

    async def get_user_tenants(self, user_id: str) -> List[str]:
        """Récupère les IDs des tenants auxquels un utilisateur appartient."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLMembershipModel.tenant_id)
                .where(SQLMembershipModel.user_id == user_id)
                .distinct()
            )
            return [row[0] for row in result.all()]

    async def get_users_with_role(
        self,
        role_id: str,
        tenant_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """Récupère les IDs des utilisateurs ayant un rôle."""
        async with self._db.session() as session:
            query = (
                select(SQLMembershipModel.user_id)
                .where(SQLMembershipModel.role_id == role_id)
            )

            if tenant_id is not None:
                query = query.where(SQLMembershipModel.tenant_id == tenant_id)

            query = query.distinct().offset(skip).limit(limit)

            result = await session.execute(query)
            return [row[0] for row in result.all()]

    async def user_has_role(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
    ) -> bool:
        """Vérifie si un utilisateur a un rôle dans un tenant."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(SQLMembershipModel.id)).where(
                    SQLMembershipModel.user_id == user_id,
                    SQLMembershipModel.tenant_id == tenant_id,
                    SQLMembershipModel.role_id == role_id,
                )
            )
            return result.scalar_one() > 0

    async def user_has_role_by_name(
        self,
        user_id: str,
        role_name: str,
        tenant_id: str,
    ) -> bool:
        """Vérifie si un utilisateur a un rôle par son nom dans un tenant."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(SQLMembershipModel.id))
                .join(self._model_class, self._model_class.id == SQLMembershipModel.role_id)
                .where(
                    SQLMembershipModel.user_id == user_id,
                    SQLMembershipModel.tenant_id == tenant_id,
                    self._model_class.name == role_name,
                )
            )
            return result.scalar_one() > 0

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
        async with self._db.session() as session:
            # Supprimer les memberships existants pour ce tenant
            await session.execute(
                delete(SQLMembershipModel).where(
                    SQLMembershipModel.user_id == user_id,
                    SQLMembershipModel.tenant_id == tenant_id,
                )
            )

            # Ajouter les nouveaux memberships
            for role_id in role_ids:
                membership = SQLMembershipModel(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    role_id=role_id,
                )
                session.add(membership)

            await session.flush()
            logger.debug(f"Rôles mis à jour pour user {user_id} dans tenant {tenant_id}: {role_ids}")
            return True

    async def clear_user_roles(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Supprime les rôles d'un utilisateur."""
        async with self._db.session() as session:
            query = delete(SQLMembershipModel).where(SQLMembershipModel.user_id == user_id)

            if tenant_id is not None:
                query = query.where(SQLMembershipModel.tenant_id == tenant_id)

            await session.execute(query)
            logger.debug(f"Memberships supprimés pour user {user_id}" + (f" dans tenant {tenant_id}" if tenant_id else ""))
            return True

    async def get_tenant_members(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """Récupère les IDs des utilisateurs membres d'un tenant."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLMembershipModel.user_id)
                .where(SQLMembershipModel.tenant_id == tenant_id)
                .distinct()
                .offset(skip)
                .limit(limit)
            )
            return [row[0] for row in result.all()]

    async def count_tenant_members(self, tenant_id: str) -> int:
        """Compte le nombre de membres d'un tenant."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(func.distinct(SQLMembershipModel.user_id)))
                .where(SQLMembershipModel.tenant_id == tenant_id)
            )
            return result.scalar_one()

    # ==========================================
    # Vérifications pour la suppression
    # ==========================================

    async def count_roles_with_permission(self, permission_name: str) -> int:
        """Compte le nombre de rôles qui utilisent une permission."""
        async with self._db.session() as session:
            result = await session.execute(select(self._model_class))
            models = result.scalars().all()

            count = 0
            for model in models:
                if model.permissions and permission_name in model.permissions:
                    count += 1
            return count
