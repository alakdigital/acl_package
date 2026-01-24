"""
Repository MySQL pour les permissions.

Implémentation asynchrone utilisant SQLAlchemy 2.0.
Partage le même code que PostgreSQL grâce à l'abstraction SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func, or_

from alak_acl.permissions.application.interface.permission_repository import IPermissionRepository
from alak_acl.permissions.domain.entities.permission import Permission
from alak_acl.permissions.infrastructure.mappers.permission_mapper import PermissionMapper
from alak_acl.permissions.infrastructure.models.sql_model import SQLPermissionModel
from alak_acl.shared.database.mysql import MySQLDatabase
from alak_acl.shared.exceptions import PermissionAlreadyExistsError, PermissionNotFoundError


from alak_acl.shared.logging import logger


class MySQLPermissionRepository(IPermissionRepository):
    """
    Implémentation du repository des permissions pour MySQL.

    Utilise SQLAlchemy 2.0 async pour les opérations de base de données.
    """

    def __init__(self, db: MySQLDatabase):
        """
        Initialise le repository.

        Args:
            db: Instance de MySQLDatabase
        """
        self._db = db
        self._mapper = PermissionMapper()

    # ============================================
    # CRUD Operations
    # ============================================

    async def create_permission(self, permission: Permission) -> Permission:
        """Crée une nouvelle permission."""
        async with self._db.session() as session:
            existing = await session.execute(
                select(SQLPermissionModel).where(
                    SQLPermissionModel.name == permission.name
                )
            )
            if existing.scalar_one_or_none():
                raise PermissionAlreadyExistsError(
                    f"Permission '{permission.name}' existe déjà"
                )

            model = self._mapper.to_sql_model(permission)
            session.add(model)
            await session.commit()
            await session.refresh(model)

            logger.debug(f"Permission créée: {permission.name}")
            return self._mapper.to_entity(model)

    async def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """Récupère une permission par son ID."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel).where(
                    SQLPermissionModel.id == permission_id
                )
            )
            model = result.scalar_one_or_none()
            if model:
                return self._mapper.to_entity(model)
            return None

    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Récupère une permission par son nom (resource:action)."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel).where(
                    SQLPermissionModel.name == name.lower()
                )
            )
            model = result.scalar_one_or_none()
            if model:
                return self._mapper.to_entity(model)
            return None

    async def update_permission(self, permission: Permission) -> Permission:
        """Met à jour une permission existante."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel).where(
                    SQLPermissionModel.id == permission.id
                )
            )
            model = result.scalar_one_or_none()

            if not model:
                raise PermissionNotFoundError(
                    f"Permission non trouvée: {permission.id}"
                )

            model.display_name = permission.display_name
            model.description = permission.description
            model.category = permission.category
            model.is_active = permission.is_active
            model.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(model)

            logger.debug(f"Permission mise à jour: {permission.name}")
            return self._mapper.to_entity(model)

    async def delete_permission(self, permission_id: str) -> bool:
        """Supprime une permission."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel).where(
                    SQLPermissionModel.id == permission_id
                )
            )
            model = result.scalar_one_or_none()

            if not model:
                return False

            if model.is_system:
                raise PermissionNotFoundError(
                    "Impossible de supprimer une permission système"
                )

            await session.delete(model)
            await session.commit()

            logger.debug(f"Permission supprimée: {model.name}")
            return True

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
        async with self._db.session() as session:
            query = select(SQLPermissionModel)

            if is_active is not None:
                query = query.where(SQLPermissionModel.is_active == is_active)
            if category:
                query = query.where(SQLPermissionModel.category == category)
            if resource:
                query = query.where(SQLPermissionModel.resource == resource)

            query = query.order_by(
                SQLPermissionModel.category,
                SQLPermissionModel.resource,
                SQLPermissionModel.action,
            ).offset(skip).limit(limit)

            result = await session.execute(query)
            models = result.scalars().all()

            return [self._mapper.to_entity(m) for m in models]

    async def count_permissions(
        self,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> int:
        """Compte le nombre de permissions."""
        async with self._db.session() as session:
            query = select(func.count(SQLPermissionModel.id))

            if is_active is not None:
                query = query.where(SQLPermissionModel.is_active == is_active)
            if category:
                query = query.where(SQLPermissionModel.category == category)
            if resource:
                query = query.where(SQLPermissionModel.resource == resource)

            result = await session.execute(query)
            return result.scalar() or 0

    async def get_by_resource(self, resource: str) -> List[Permission]:
        """Récupère toutes les permissions d'une ressource."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel)
                .where(SQLPermissionModel.resource == resource.lower())
                .where(SQLPermissionModel.is_active == True)
                .order_by(SQLPermissionModel.action)
            )
            models = result.scalars().all()
            return [self._mapper.to_entity(m) for m in models]

    async def get_by_category(self, category: str) -> List[Permission]:
        """Récupère toutes les permissions d'une catégorie."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel)
                .where(SQLPermissionModel.category == category)
                .where(SQLPermissionModel.is_active == True)
                .order_by(SQLPermissionModel.resource, SQLPermissionModel.action)
            )
            models = result.scalars().all()
            return [self._mapper.to_entity(m) for m in models]

    async def get_all_resources(self) -> List[str]:
        """Récupère la liste de toutes les ressources distinctes."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel.resource)
                .distinct()
                .order_by(SQLPermissionModel.resource)
            )
            return [row[0] for row in result.all()]

    async def get_all_categories(self) -> List[str]:
        """Récupère la liste de toutes les catégories distinctes."""
        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel.category)
                .where(SQLPermissionModel.category.isnot(None))
                .distinct()
                .order_by(SQLPermissionModel.category)
            )
            return [row[0] for row in result.all() if row[0]]

    # ============================================
    # Bulk Operations
    # ============================================

    async def create_many(self, permissions: List[Permission]) -> List[Permission]:
        """Crée plusieurs permissions en une seule opération."""
        async with self._db.session() as session:
            created = []
            for permission in permissions:
                existing = await session.execute(
                    select(SQLPermissionModel).where(
                        SQLPermissionModel.name == permission.name
                    )
                )
                if existing.scalar_one_or_none():
                    logger.debug(f"Permission existe déjà: {permission.name}")
                    continue

                model = self._mapper.to_sql_model(permission)
                session.add(model)
                created.append(permission)

            await session.commit()
            logger.info(f"{len(created)} permissions créées")
            return created

    async def get_by_ids(self, permission_ids: List[str]) -> List[Permission]:
        """Récupère plusieurs permissions par leurs IDs."""
        if not permission_ids:
            return []

        async with self._db.session() as session:
            result = await session.execute(
                select(SQLPermissionModel).where(
                    SQLPermissionModel.id.in_(permission_ids)
                )
            )
            models = result.scalars().all()
            return [self._mapper.to_entity(m) for m in models]

    async def get_by_names(self, names: List[str]) -> List[Permission]:
        """Récupère plusieurs permissions par leurs noms."""
        if not names:
            return []

        async with self._db.session() as session:
            normalized_names = [n.lower() for n in names]
            result = await session.execute(
                select(SQLPermissionModel).where(
                    SQLPermissionModel.name.in_(normalized_names)
                )
            )
            models = result.scalars().all()
            return [self._mapper.to_entity(m) for m in models]

    # ============================================
    # Utility Methods
    # ============================================

    async def permission_exists(self, name: str) -> bool:
        """Vérifie si une permission existe par son nom."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(SQLPermissionModel.id)).where(
                    SQLPermissionModel.name == name.lower()
                )
            )
            return (result.scalar() or 0) > 0

    async def search_permissions(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Permission]:
        """Recherche des permissions par texte."""
        async with self._db.session() as session:
            search_pattern = f"%{query.lower()}%"
            result = await session.execute(
                select(SQLPermissionModel)
                .where(
                    or_(
                        SQLPermissionModel.name.like(search_pattern),
                        SQLPermissionModel.display_name.like(search_pattern),
                        SQLPermissionModel.description.like(search_pattern),
                    )
                )
                .order_by(SQLPermissionModel.name)
                .offset(skip)
                .limit(limit)
            )
            models = result.scalars().all()
            return [self._mapper.to_entity(m) for m in models]
