"""
Utilitaires pour la gestion du cache ACL.

Fournit des fonctions et décorateurs pour gérer le cache
de manière cohérente dans tout le package.
"""

from enum import Enum
from functools import wraps
import hashlib
import json
import inspect
from typing import Any, Callable, Optional

from pydantic import BaseModel

from alak_acl.shared.logging import logger


class CachePrefix(str, Enum):
    """Préfixes de cache pour les différentes entités ACL."""
    USER_ME = "user_me"
    USER_ROLES = "user_roles"
    USER_TENANTS = "user_tenants"
    ROLE = "role"
    PERMISSION = "permission"


def generate_hash(data: dict) -> str:
    """
    Génère un hash court à partir d'un dictionnaire.

    Args:
        data: Dictionnaire à hasher

    Returns:
        Hash MD5 tronqué (8 caractères)
    """
    json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(json_str.encode()).hexdigest()[:8]


def serialize_params(params: dict) -> dict:
    """
    Nettoie et sérialise les paramètres pour le cache.

    Args:
        params: Paramètres de la fonction

    Returns:
        Dictionnaire sérialisable
    """
    serializable = {}

    for key, value in params.items():
        # Ignorer les dépendances FastAPI et paramètres techniques
        if key.endswith("_usecase") or key.endswith("_repository"):
            continue
        if key in ("current_user", "config", "db", "cache"):
            continue
        if key.startswith("_"):
            continue

        # Pydantic v2
        if hasattr(value, "model_dump"):
            serializable.update(value.model_dump(mode="json"))
            continue

        # Types simples
        if isinstance(value, (str, int, float, bool, type(None))):
            serializable[key] = value
            continue

        # List / Dict / Tuple
        if isinstance(value, (list, dict, tuple)):
            serializable[key] = json.loads(
                json.dumps(value, default=str)
            )

    return serializable


def build_cache_key(
    prefix: CachePrefix,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    params: Optional[dict] = None,
) -> str:
    """
    Génère une clé de cache cohérente.

    Format: ALAKACL:{prefix}:{user_id}:{tenant_id}:{params_hash}

    Args:
        prefix: Préfixe de cache (CachePrefix enum)
        user_id: ID de l'utilisateur (optionnel)
        tenant_id: ID du tenant (optionnel)
        params: Paramètres additionnels (optionnel)

    Returns:
        Clé de cache formatée
    """
    parts = ["ALAKACL", prefix.value]

    if user_id:
        parts.append(user_id)

    if tenant_id:
        parts.append(f"tenant:{tenant_id}")
    else:
        parts.append("global")

    if params:
        params_hash = generate_hash(params)
        parts.append(params_hash)

    return ":".join(parts)


async def invalidate_user_cache(
    user_id: str,
    tenant_id: Optional[str] = None,
    prefix: CachePrefix = CachePrefix.USER_ME,
) -> None:
    """
    Invalide le cache d'un utilisateur.

    Args:
        user_id: ID de l'utilisateur
        tenant_id: ID du tenant (si None, invalide tous les tenants)
        prefix: Préfixe de cache à invalider
    """
    try:
        from alak_acl.shared.cache.factory import get_cache
        cache = get_cache()

        if tenant_id:
            # Invalider uniquement pour ce tenant
            pattern = f"ALAKACL:{prefix.value}:{user_id}:tenant:{tenant_id}*"
        else:
            # Invalider tous les tenants de cet utilisateur
            pattern = f"ALAKACL:{prefix.value}:{user_id}:*"

        deleted = await cache.scan_and_delete(pattern)
        logger.info(f"[CACHE INVALIDATE] {prefix.value} - User: {user_id} - {deleted} clés supprimées")

    except Exception as e:
        logger.warning(f"Erreur invalidation cache user {user_id}: {e}")


async def set_user_cache(
    user_id: str,
    data: Any,
    tenant_id: Optional[str] = None,
    prefix: CachePrefix = CachePrefix.USER_ME,
    ttl: Optional[int] = None,
) -> None:
    """
    Stocke des données utilisateur en cache.

    Args:
        user_id: ID de l'utilisateur
        data: Données à mettre en cache
        tenant_id: ID du tenant (optionnel)
        prefix: Préfixe de cache
        ttl: Durée de vie en secondes
    """
    try:
        from alak_acl.shared.cache.factory import get_cache
        cache = get_cache()

        cache_key = build_cache_key(prefix, user_id, tenant_id)

        # Sérialiser si Pydantic
        cache_value = data
        if hasattr(data, "model_dump"):
            cache_value = data.model_dump(mode="json")
        elif hasattr(data, "dict"):
            cache_value = data.dict()

        await cache.set(cache_key, cache_value, ttl=ttl)
        logger.debug(f"[CACHE SET] {prefix.value} - User: {user_id}")

    except Exception as e:
        logger.warning(f"Erreur écriture cache user {user_id}: {e}")


async def get_user_cache(
    user_id: str,
    tenant_id: Optional[str] = None,
    prefix: CachePrefix = CachePrefix.USER_ME,
) -> Optional[Any]:
    """
    Récupère des données utilisateur du cache.

    Args:
        user_id: ID de l'utilisateur
        tenant_id: ID du tenant (optionnel)
        prefix: Préfixe de cache

    Returns:
        Données en cache ou None
    """
    try:
        from alak_acl.shared.cache.factory import get_cache
        cache = get_cache()

        cache_key = build_cache_key(prefix, user_id, tenant_id)
        cached = await cache.get(cache_key)

        if cached:
            logger.debug(f"[CACHE HIT] {prefix.value} - User: {user_id}")
        else:
            logger.debug(f"[CACHE MISS] {prefix.value} - User: {user_id}")

        return cached

    except Exception as e:
        logger.warning(f"Erreur lecture cache user {user_id}: {e}")
        return None


async def invalidate_all_user_caches(user_id: str, tenant_id: Optional[str] = None) -> None:
    """
    Invalide tous les caches liés à un utilisateur (USER_ME, USER_ROLES, USER_TENANTS).

    Args:
        user_id: ID de l'utilisateur
        tenant_id: ID du tenant (si None, invalide tous les tenants)
    """
    for prefix in [CachePrefix.USER_ME, CachePrefix.USER_ROLES, CachePrefix.USER_TENANTS]:
        await invalidate_user_cache(user_id, tenant_id, prefix)


async def set_cache(
    key: str,
    data: Any,
    ttl: Optional[int] = None,
) -> None:
    """
    Stocke des données en cache avec une clé personnalisée.

    Args:
        key: Clé de cache
        data: Données à mettre en cache
        ttl: Durée de vie en secondes
    """
    try:
        from alak_acl.shared.cache.factory import get_cache
        cache = get_cache()

        # Sérialiser si Pydantic ou liste de Pydantic
        cache_value = data
        if hasattr(data, "model_dump"):
            cache_value = data.model_dump(mode="json")
        elif isinstance(data, list) and data and hasattr(data[0], "model_dump"):
            cache_value = [item.model_dump(mode="json") for item in data]

        await cache.set(key, cache_value, ttl=ttl)
        logger.debug(f"[CACHE SET] {key}")

    except Exception as e:
        logger.warning(f"Erreur écriture cache {key}: {e}")


async def get_cache_value(key: str) -> Optional[Any]:
    """
    Récupère des données du cache avec une clé personnalisée.

    Args:
        key: Clé de cache

    Returns:
        Données en cache ou None
    """
    try:
        from alak_acl.shared.cache.factory import get_cache
        cache = get_cache()

        cached = await cache.get(key)

        if cached:
            logger.debug(f"[CACHE HIT] {key}")
        else:
            logger.debug(f"[CACHE MISS] {key}")

        return cached

    except Exception as e:
        logger.warning(f"Erreur lecture cache {key}: {e}")
        return None


async def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalide toutes les clés correspondant au pattern.

    Args:
        pattern: Pattern de recherche (ex: "ALAKACL:role:*")

    Returns:
        Nombre de clés supprimées
    """
    try:
        from alak_acl.shared.cache.factory import get_cache
        cache = get_cache()

        deleted = await cache.scan_and_delete(pattern)
        logger.info(f"[CACHE INVALIDATE] Pattern: {pattern} - {deleted} clés supprimées")
        return deleted

    except Exception as e:
        logger.warning(f"Erreur invalidation cache pattern {pattern}: {e}")
        return 0
