"""
Repository PostgreSQL pour l'authentification.

Supporte les modèles personnalisés avec colonnes supplémentaires.
"""

from typing import Optional, List, Type

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from ...application.interface.auth_repository import IAuthRepository
from ...domain.entities.auth_user import AuthUser
from ..models.sql_model import SQLAuthUserModel
from ..mappers.auth_user_mapper import AuthUserMapper
from ....shared.database.postgresql import PostgreSQLDatabase
from ....shared.exceptions import UserAlreadyExistsError, UserNotFoundError
from ....shared.logging import logger


class PostgreSQLAuthRepository(IAuthRepository):
    """
    Implémentation du repository d'authentification pour PostgreSQL.

    Utilise SQLAlchemy 2.0 async avec asyncpg.
    Supporte les modèles utilisateur personnalisés avec colonnes supplémentaires.

    Attributes:
        db: Instance de connexion PostgreSQL
        model_class: Classe du modèle utilisateur (par défaut ou personnalisée)
        mapper: Instance du mapper (configuré pour le modèle personnalisé)

    Example:
        ```python
        # Avec modèle personnalisé
        from sqlalchemy import Column, String
        from fastapi_acl.auth.infrastructure.models import SQLAuthUserModel

        class CustomUserModel(SQLAuthUserModel):
            __tablename__ = "users"
            phone = Column(String(20), nullable=True)
            company = Column(String(100), nullable=True)

        repo = PostgreSQLAuthRepository(
            db=database,
            model_class=CustomUserModel,
        )
        ```
    """

    def __init__(
        self,
        db: PostgreSQLDatabase,
        model_class: Type[SQLAuthUserModel] = SQLAuthUserModel,
        mapper: Optional[AuthUserMapper] = None,
    ):
        """
        Initialise le repository.

        Args:
            db: Instance de PostgreSQLDatabase
            model_class: Classe du modèle utilisateur (par défaut ou personnalisée)
            mapper: Instance du mapper personnalisée (optionnel)
        """
        self._db = db
        self._model_class = model_class
        self._mapper = mapper or AuthUserMapper(sql_model_class=model_class)

    @property
    def model_class(self) -> Type[SQLAuthUserModel]:
        """Retourne la classe du modèle utilisé."""
        return self._model_class

    async def create_user(self, user: AuthUser) -> AuthUser:
        """
        Crée un nouvel utilisateur.

        Les champs personnalisés dans extra_fields sont automatiquement
        mappés vers les colonnes correspondantes du modèle.
        """
        model = self._mapper.to_sql_model(user, self._model_class)

        async with self._db.session() as session:
            try:
                session.add(model)
                await session.flush()
                await session.refresh(model)
                logger.debug(f"Utilisateur créé: {user.username}")
                return self._mapper.to_entity(model)
            except IntegrityError as e:
                logger.warning(f"Erreur d'intégrité lors de la création: {e}")
                raise UserAlreadyExistsError(
                    "Un utilisateur avec ce username ou email existe déjà"
                )

    async def get_by_id(self, user_id: str) -> Optional[AuthUser]:
        """Récupère un utilisateur par son ID (string UUID)."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.id == user_id)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._mapper.to_entity(model)
            return None

    async def get_by_username(self, username: str) -> Optional[AuthUser]:
        """Récupère un utilisateur par son username."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.username == username)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._mapper.to_entity(model)
            return None

    async def get_by_email(self, email: str) -> Optional[AuthUser]:
        """Récupère un utilisateur par son email."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.email == email)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._mapper.to_entity(model)
            return None

    async def update_user(self, user: AuthUser) -> AuthUser:
        """
        Met à jour un utilisateur.

        Les champs personnalisés dans extra_fields sont automatiquement
        mis à jour dans les colonnes correspondantes.
        """
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.id == user.id)
            )
            model = result.scalar_one_or_none()

            if not model:
                raise UserNotFoundError(f"Utilisateur non trouvé: {user.id}")

            self._mapper.update_sql_model(model, user)
            await session.flush()
            await session.refresh(model)

            logger.debug(f"Utilisateur mis à jour: {user.username}")
            return self._mapper.to_entity(model)

    async def delete_user(self, user_id: str) -> bool:
        """Supprime un utilisateur par son ID (string UUID)."""
        async with self._db.session() as session:
            result = await session.execute(
                select(self._model_class).where(self._model_class.id == user_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return False

            await session.delete(model)
            logger.debug(f"Utilisateur supprimé: {user_id}")
            return True

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[AuthUser]:
        """Liste les utilisateurs avec pagination."""
        async with self._db.session() as session:
            query = select(self._model_class)

            if is_active is not None:
                query = query.where(self._model_class.is_active == is_active)

            query = query.offset(skip).limit(limit).order_by(self._model_class.created_at.desc())

            result = await session.execute(query)
            models = result.scalars().all()

            return [self._mapper.to_entity(model) for model in models]

    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """Compte le nombre d'utilisateurs."""
        async with self._db.session() as session:
            query = select(func.count(self._model_class.id))

            if is_active is not None:
                query = query.where(self._model_class.is_active == is_active)

            result = await session.execute(query)
            return result.scalar_one()

    async def username_exists(self, username: str) -> bool:
        """Vérifie si un username existe."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(self._model_class.id)).where(
                    self._model_class.username == username
                )
            )
            return result.scalar_one() > 0

    async def email_exists(self, email: str) -> bool:
        """Vérifie si un email existe."""
        async with self._db.session() as session:
            result = await session.execute(
                select(func.count(self._model_class.id)).where(
                    self._model_class.email == email
                )
            )
            return result.scalar_one() > 0

    async def find_by_extra_field(
        self,
        field_name: str,
        value: any,
    ) -> Optional[AuthUser]:
        """
        Recherche un utilisateur par un champ personnalisé.

        Args:
            field_name: Nom du champ personnalisé
            value: Valeur à rechercher

        Returns:
            Utilisateur trouvé ou None

        Raises:
            ValueError: Si le champ n'existe pas dans le modèle
        """
        if not hasattr(self._model_class, field_name):
            raise ValueError(f"Le champ '{field_name}' n'existe pas dans le modèle")

        async with self._db.session() as session:
            column = getattr(self._model_class, field_name)
            result = await session.execute(
                select(self._model_class).where(column == value)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._mapper.to_entity(model)
            return None

    async def list_by_extra_field(
        self,
        field_name: str,
        value: any,
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
        if not hasattr(self._model_class, field_name):
            raise ValueError(f"Le champ '{field_name}' n'existe pas dans le modèle")

        async with self._db.session() as session:
            column = getattr(self._model_class, field_name)
            query = (
                select(self._model_class)
                .where(column == value)
                .offset(skip)
                .limit(limit)
                .order_by(self._model_class.created_at.desc())
            )

            result = await session.execute(query)
            models = result.scalars().all()

            return [self._mapper.to_entity(model) for model in models]
