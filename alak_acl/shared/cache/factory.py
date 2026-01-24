"""
Factory pour créer le backend de cache.
"""

from typing import Union

from alak_acl.shared.cache.base import CacheBackend
from alak_acl.shared.cache.redis_cache import RedisCache
from alak_acl.shared.cache.memory_cache import MemoryCache
from alak_acl.shared.config import ACLConfig
from alak_acl.shared.exceptions import ConfigurationError, CacheConnectionError
from alak_acl.shared.logging import logger


CacheType = Union[RedisCache, MemoryCache]


class CacheFactory:
    """
    Factory pour créer le backend de cache approprié.

    Gère le fallback automatique vers le cache mémoire
    si Redis n'est pas disponible.
    """

    @staticmethod
    async def create(config: ACLConfig) -> CacheType:
        """
        Crée une instance de cache selon la configuration.

        Si Redis est configuré mais indisponible, utilise
        automatiquement le cache mémoire comme fallback.

        Args:
            config: Configuration ACL

        Returns:
            Instance de cache (Redis ou Memory)
        """
        if not config.enable_cache:
            logger.info("Cache désactivé, utilisation du cache mémoire minimal")
            cache = MemoryCache(default_ttl=config.cache_ttl)
            await cache.connect()
            return cache

        if config.cache_backend == "redis" and config.redis_url:
            try:
                cache = RedisCache(
                    url=config.redis_url,
                    default_ttl=config.cache_ttl,
                )
                await cache.connect()
                return cache

            except CacheConnectionError as e:
                logger.warning(
                    f"Redis indisponible: {e}. Fallback vers cache mémoire."
                )

        # Fallback vers cache mémoire
        logger.info("Utilisation du cache mémoire")
        cache = MemoryCache(default_ttl=config.cache_ttl)
        await cache.connect()
        return cache


# Instance globale (initialisée par ACLManager)
_cache: CacheType | None = None


def get_cache() -> CacheType:
    """
    Retourne l'instance globale du cache.

    Returns:
        Instance de cache

    Raises:
        ConfigurationError: Si le cache n'est pas initialisé
    """
    if _cache is None:
        raise ConfigurationError(
            "Cache non initialisé. Appelez ACLManager.initialize() d'abord."
        )
    return _cache


def set_cache(cache: CacheType) -> None:
    """
    Définit l'instance globale du cache.

    Args:
        cache: Instance de cache
    """
    global _cache
    _cache = cache
