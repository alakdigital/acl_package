"""
Repository PostgreSQL pour les rôles.
"""

from typing import Optional, List, Type

from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError


from alak_acl.roles.application.interface.role_repository import IRoleRepository
from alak_acl.roles.domain.entities.role import Role
from alak_acl.roles.infrastructure.mappers.role_mapper import RoleMapper
from alak_acl.roles.infrastructure.models.sql_model import SQLRoleModel, SQLUserRoleModel
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
                raise RoleAlreadyExistsError(f"Un rôle avec le nom '{role.name}' existe déjà")

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
                raise RoleNotFoundError(f"Rôle non trouvé: {role.id}")

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
        - Le rôle ne doit pas être assigné à des utilisateurs
        - Le rôle ne doit pas avoir de permissions associées

        Raises:
            PermissionDeniedError: Si c'est un rôle système
            RoleInUseError: Si le rôle est assigné à des utilisateurs ou a des permissions
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

            # Vérifier si le rôle est assigné à des utilisateurs
            user_count_result = await session.execute(
                select(func.count(SQLUserRoleModel.user_id)).where(
                    SQLUserRoleModel.role_id == role_id
                )
            )
            user_count = user_count_result.scalar_one()
            if user_count > 0:
                raise RoleInUseError(
                    f"Impossible de supprimer le rôle: il est assigné à {user_count} utilisateur(s)"
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
    ) -> List[Role]:
        """Liste les rôles avec pagination."""
        async with self._db.session() as session:
            query = select(self._model_class)

            if is_active is not None:
                query = query.where(self._model_class.is_active == is_active)

            query = query.offset(skip).limit(limit).order_by(
                self._model_class.priority.desc(),
                self._model_class.name.asc()
            )

            result = await session.execute(query)
            models = result.scalars().all()

            return [self._mapper.to_entity(model) for model in models]

    async def count_roles(self, is_active: Optional[bool] = None) -> int:
        """Compte le nombre de rôles."""
        async with self._db.session() as session:
            query = select(func.count(self._model_class.id))

            if is_active is not None:
                query = query.where(self._model_class.is_active == is_active)

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

    # ==========================================
    # Assignation des rôles
    # ==========================================

    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assigne un rôle à un utilisateur."""
        async with self._db.session() as session:
            # Vérifier que le rôle existe
            role_result = await session.execute(
                select(self._model_class).where(self._model_class.id == role_id)
            )
            if not role_result.scalar_one_or_none():
                raise RoleNotFoundError(f"Rôle non trouvé: {role_id}")

            # Vérifier si l'association existe déjà
            existing = await session.execute(
                select(SQLUserRoleModel).where(
                    SQLUserRoleModel.user_id == user_id,
                    SQLUserRoleModel.role_id == role_id,
                )
            )
            if existing.scalar_one_or_none():
                return True  # Déjà assigné

            # Créer l'association
            user_role = SQLUserRoleModel(user_id=user_id, role_id=role_id)
            session.add(user_role)
            await session.flush()

            logger.debug(f"Rôle {role_id} assigné à l'utilisateur {user_id}")
            return True

    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Retire un rôle d'un utilisateur."""
        async with self._db.session() as session:
            result = await session.execute(
                delete(SQLUserRoleModel).where(
                    SQLUserRoleModel.user_id == user_id,
                    SQLUserRoleModel.role_id == role_id,
                )
            )
            deleted = result.rowcount > 0

            if deleted:
                logger.debug(f"Rôle {role_id} retiré de l'utilisateur {user_id}")

            return deleted

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Récupère tous les rôles d'un utilisateur."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class)
                .join(SQLUserRoleModel, SQLUserRoleModel.role_id == self._model_class.id)
                .where(SQLUserRoleModel.user_id == user_id)
                .order_by(self._model_class.priority.desc())
            )
            models = result.scalars().all()
            return [self._mapper.to_entity(model) for model in models]

    async def get_users_with_role(
        self,
        role_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[str]:
        """Récupère les IDs des utilisateurs ayant un rôle."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLUserRoleModel.user_id)
                .where(SQLUserRoleModel.role_id == role_id)
                .offset(skip)
                .limit(limit)
            )
            return [row[0] for row in result.all()]

    async def user_has_role(self, user_id: str, role_id: str) -> bool:
        """Vérifie si un utilisateur a un rôle."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(SQLUserRoleModel.user_id)).where(
                    SQLUserRoleModel.user_id == user_id,
                    SQLUserRoleModel.role_id == role_id,
                )
            )
            return result.scalar_one() > 0

    async def user_has_role_by_name(self, user_id: str, role_name: str) -> bool:
        """Vérifie si un utilisateur a un rôle par son nom."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(SQLUserRoleModel.user_id))
                .join(self._model_class, self._model_class.id == SQLUserRoleModel.role_id)
                .where(
                    SQLUserRoleModel.user_id == user_id,
                    self._model_class.name == role_name,
                )
            )
            return result.scalar_one() > 0

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
        async with self._db.session() as session:
            # Supprimer tous les rôles existants
            await session.execute(
                delete(SQLUserRoleModel).where(SQLUserRoleModel.user_id == user_id)
            )

            # Ajouter les nouveaux rôles
            for role_id in role_ids:
                user_role = SQLUserRoleModel(user_id=user_id, role_id=role_id)
                session.add(user_role)

            await session.flush()
            logger.debug(f"Rôles mis à jour pour l'utilisateur {user_id}: {role_ids}")
            return True

    async def clear_user_roles(self, user_id: str) -> bool:
        """Supprime tous les rôles d'un utilisateur."""
        async with self._db.session() as session:
            result = await session.execute(
                delete(SQLUserRoleModel).where(SQLUserRoleModel.user_id == user_id)
            )
            logger.debug(f"Rôles supprimés pour l'utilisateur {user_id}")
            return True
