"""
Module cache - Gestion du cache Redis et mémoire.

Fournit une abstraction pour le cache avec fallback automatique.
"""

from alak_acl.shared.cache.base import CacheBackend
from alak_acl.shared.cache.redis_cache import RedisCache
from alak_acl.shared.cache.memory_cache import MemoryCache
from alak_acl.shared.cache.factory import CacheFactory, get_cache
from alak_acl.shared.cache.utils import (
    CachePrefix,
    build_cache_key,
    invalidate_user_cache,
    invalidate_all_user_caches,
    invalidate_cache_pattern,
    set_user_cache,
    get_user_cache,
    set_cache,
    get_cache_value,
)

__all__ = [
    "CacheBackend",
    "RedisCache",
    "MemoryCache",
    "CacheFactory",
    "get_cache",
    "CachePrefix",
    "build_cache_key",
    "invalidate_user_cache",
    "invalidate_all_user_caches",
    "invalidate_cache_pattern",
    "set_user_cache",
    "get_user_cache",
    "set_cache",
    "get_cache_value",
]
