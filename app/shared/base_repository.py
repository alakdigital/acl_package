"""Repository de base pour les opérations SQLAchemy."""
from typing import List, Optional, Any, Tuple, Type
from datetime import datetime, timezone
from sqlalchemy import delete as mysql_delete, desc, func, select, update as mysql_update
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:
    """Classe de base avec les opérations CRUD communes pour MongoDB."""

    def __init__(self, session: AsyncSession, model: Type):
        self.session = session
        self.model = model

    async def create(self, data: dict[str, Any]) -> Any:
        """Crée un objet dans la base de données."""
        
        data["created_at"] = datetime.now(timezone.utc)
        data["updated_at"] = None
        data.pop('id', None)  # Supprimer l'ID s'il existe pour éviter les conflits
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def find_by_id(self, id: str, options: Optional[List[Any]] = None) -> Optional[Any]:
        """Trouve un objet par son ID."""
        stm = select(self.model).where(self.model.id == id)
        if options:
            stm = stm.options(*options)
        obj = await self.session.execute(stm)
        return obj.scalar_one_or_none()


    async def find_one(self, filters: dict[str, Any], options: Optional[List[Any]] = None) -> Optional[Any]:
        """Trouve un objet selon des filtres.

        Args:
            filters: Dictionnaire de filtres
            options: Liste d'options de chargement (ex: selectinload, joinedload)
        """
        stm = select(self.model).filter_by(**filters)
        if options:
            stm = stm.options(*options)
        result = await self.session.execute(stm)
        return result.scalars().first()
    
    
    async def find_many(
        self,
        skip: int = 0,
        limit: int = 20,
        sort: Optional[List[Any]] = None,
        options: Optional[List[Any]] = None,
        **filters
    ) -> Tuple[int, List[Any]]:

        """Trouve plusieurs objets selon des filtres.

        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            sort: Liste de colonnes pour le tri
            options: Liste d'options de chargement (ex: selectinload, joinedload)
            **filters: Filtres à appliquer
        """
        stmt = select(self.model).filter_by(**filters).offset(skip).limit(limit)
        if sort:
            stmt = stmt.order_by(desc(*sort))
        if options:
            stmt = stmt.options(*options)
        result = await self.session.execute(stmt)
        count = await self.count()
        return count, result.scalars().all()


    async def count(self, **filters) -> int:
        """Compte les objets selon des filtres."""
        base_query = select(self.model).filter_by(**filters)
        total = (await self.session.execute(
                select(func.count()).select_from(base_query.subquery())
            )).scalar_one()
        return total


    async def update(self, obj_id: Any, data: dict[str, Any]) -> bool:
        """Met à jour un objet."""
        obj = await self.find_by_id(obj_id)
        if not obj:
            return False  # objet non trouvé

        # Filtrer les champs None
        clean_data = {k: v for k, v in data.items() if v is not None}
        if not clean_data:
            return False
        
        # Appliquer les modifications
        for key, value in clean_data.items():
            setattr(obj, key, value)

        # Mettre à jour updated_at
        setattr(obj, "updated_at", datetime.now(timezone.utc))
     
        await self.session.flush()
        await self.session.refresh(obj)
        return obj is not None


    async def delete(self, obj_id: Any) -> bool:
        """Supprime un objet."""
        stmt = await self.find_by_id(obj_id)
        if not stmt:
            return False
        result = await self.session.delete(stmt)
        await self.session.flush()
        return result is None 
    

    async def solf_delete(self, obj_id: Any) -> bool:
        """Soft delete"""
        result = await self.update(obj_id=obj_id, data={'deleted': True})
        return result is None 


    async def exists(self, **filters) -> bool:
        """Vérifie si un objet existe."""
        obj = await self.find_one(**filters)
        return obj is not None