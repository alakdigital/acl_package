"""Configuration Redis pour le caching."""
import asyncio
from enum import Enum
import hashlib
import redis.asyncio as redis
from typing import Optional, Any
import json
from app.core.config import settings



class CachePrefix(Enum):
    """Énumération des préfixes de cache pour éviter les erreurs de frappe"""
    CLIENTS = "Clients"
    USERS = "Users"
    USER_DETAIL = "UserDetail"
    CURRENT_USER = "CurrentUser"
    PRODUCT_LIST = "ProductList"
    PRODUCT_DETAIL = "ProductDetail"
    BRAND_LIST = "BrandList"
    BRAND_DETAIL = "BrandDetail"
    
    # CATEGORIE
    CATEGORY_LIST = "CategoryList"
    CATEGORY_DETAIL = "CategoryDetail"
 

class RedisCache:
    """Gestionnaire de cache Redis."""

    client: Optional[redis.Redis] = None
    # Cache local pour éviter les appels répétés
    
    def __init__(self):
        self._filter_hash_cache = {}

    async def connect(self) -> None:
        """établit la connexion à Redis."""
        self.client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        print(" Connecté à Redis")

    async def disconnect(self) -> None:
        """Ferme la connexion à Redis."""
        if self.client:
            await self.client.close()
            print("= Déconnecté de Redis")

    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        if not self.client:
            return None
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        Stocke une valeur dans le cache.

        Args:
            key: Clé du cache
            value: Valeur à stocker
            expire: Temps d'expiration en secondes
        """
        if not self.client:
            return False

        if isinstance(value, (dict, list)):
            value = json.dumps(value)
            

        if expire:
            return await self.client.setex(key, expire, value)
        else:
            return await self.client.set(key, value)

    async def delete(self, key: str) -> bool:
        """Supprime une clé du cache."""
        if not self.client:
            return False
        return await self.client.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache."""
        if not self.client:
            return False
        return await self.client.exists(key) > 0

    def _generate_filter_hash(self, filters: Optional[dict]) -> str:
        """Génère un hash pour les filtres avec cache local pour optimiser."""
        if not filters:
            return "nofilter"
            
        # Cache local simple pour éviter les calculs répétés
        filter_key = str(sorted(filters.items()))
        if filter_key in self._filter_hash_cache:
            return self._filter_hash_cache[filter_key]
            
        clean_filters = {
            k: json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
            for k, v in filters.items() 
            if v is not None and v != ""
        }
        
        filter_str = json.dumps(clean_filters, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        hash_value = hashlib.md5(filter_str.encode('utf-8')).hexdigest()[:16]
        
        # Éviter que le cache local devienne trop gros
        if len(self._filter_hash_cache) > 1000:
            self._filter_hash_cache.clear()
            
        self._filter_hash_cache[filter_key] = hash_value
        return hash_value



    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Supprime toutes les clés correspondant à un pattern.

        Args:
            pattern: Pattern Redis (ex: "user:*")
        """
        if not self.client:
            return 0

        keys = []
        async for key in self.client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            return await self.client.delete(*keys)
        return 0

    async def clear_all_cache(self) -> int:
        """Supprime complètement tout le cache de l'application."""
        import logging
        logger = logging.getLogger(__name__)

        logger.warning("[CACHE] Suppression complète du cache demandée")
        patterns = [f"{settings.app_redis_prefixe}:{prefix.value}:*" for prefix in CachePrefix]

        tasks = [self._scan_and_delete(p, f"pattern {p}") for p in patterns]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_deleted = sum(r for r in results if isinstance(r, int))

        # Nettoyage du cache local
        self._filter_hash_cache.clear()

        logger.warning(f"[CACHE] {total_deleted} clés supprimées au total")
        return total_deleted


redis_cache = RedisCache()


async def get_cache() -> RedisCache:
    """Dependency pour obtenir le cache Redis."""
    return redis_cache