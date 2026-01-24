"""
Module cache - Gestion du cache Redis et mémoire.

Fournit une abstraction pour le cache avec fallback automatique.
"""

from alak_acl.shared.cache.base import CacheBackend
from alak_acl.shared.cache.redis_cache import RedisCache
from alak_acl.shared.cache.memory_cache import MemoryCache
from alak_acl.shared.cache.factory import CacheFactory, get_cache

__all__ = [
    "CacheBackend",
    "RedisCache",
    "MemoryCache",
    "CacheFactory",
    "get_cache",
]
