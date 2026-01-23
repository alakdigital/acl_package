"""
Module cache - Gestion du cache Redis et mémoire.

Fournit une abstraction pour le cache avec fallback automatique.
"""

from .base import CacheBackend
from .redis_cache import RedisCache
from .memory_cache import MemoryCache
from .factory import CacheFactory, get_cache

__all__ = [
    "CacheBackend",
    "RedisCache",
    "MemoryCache",
    "CacheFactory",
    "get_cache",
]
