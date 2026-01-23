from functools import wraps
import logging
from typing import Callable, Optional
import inspect
import json

from pydantic import BaseModel
from app.core.db.redis.cache_manager import redis_cache, CachePrefix
from app.core.config import settings


logger = logging.getLogger(__name__)


def invalidate_cache(prefix: CachePrefix, param_keys: Optional[list[str]] = None):
    """
    Décorateur pour invalider le cache après exécution de la fonction.
    Extrait automatiquement le tenant_id depuis current_user si présent.

    Args:
        prefix: Prefix du cache à invalider
        param_keys: Liste des noms de paramètres à utiliser pour la clé (ex: ['id_user'])
                    Si None, invalide tout le prefix

    Exemples :
        # Invalider tout le prefix
        @invalidate_cache(prefix=CachePrefix.USER_DETAIL)
        async def update_user(...):
            ...

        # Invalider une clé spécifique basée sur id_user
        @invalidate_cache(prefix=CachePrefix.USER_DETAIL, param_keys=['id_user'])
        async def update_user(id_user: str, ...):
            ...

        # Multi-tenant: tenant_id est extrait automatiquement de current_user
        @invalidate_cache(prefix=CachePrefix.PRODUCT_LIST, param_keys=['product_id'])
        async def update_product(product_id: str, current_user: CurrentUser, ...):
            # Invalide seulement pour le tenant de current_user
            ...
    """
    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Exécuter la fonction principale
            result = await func(*args, **kwargs)

            # Récupérer les paramètres de la fonction
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            func_params = dict(bound.arguments)

            # Extraire tenant_id depuis current_user si présent
            tenant_id = None
            for param_name, param_value in func_params.items():
                if param_name == 'current_user' and hasattr(param_value, 'tenant_id'):
                    tenant_id = param_value.tenant_id
                    break

            # Invalider le cache
            if param_keys:
                # Filtrer pour garder seulement les param_keys demandés
                cache_params = {k: v for k, v in func_params.items() if k in param_keys}
                logger.debug(f"Invalidate cache params: {cache_params}")
                # Filtrer les dépendances
                serializable_params = {}
                for key, value in cache_params.items():
                    if key.endswith('_case') or key.endswith('_repository') or key.endswith('_service'):
                        continue
                    if isinstance(value, (str, int, float, bool, type(None), list, dict, tuple)):
                        serializable_params[key] = value
                print(serializable_params)
                # Ajouter tenant_id aux params si présent
                if tenant_id:
                    serializable_params['tenant_id'] = tenant_id

                # Générer la clé
                params_json = json.dumps(serializable_params, sort_keys=True, ensure_ascii=False)
                params_hash = redis_cache._generate_filter_hash({"params": params_json})
                key = f"{settings.app_redis_prefixe}:{prefix.value}:{params_hash}"

                await redis_cache.delete(key)
                log_msg = f"🗑️ [CACHE INVALIDATE] {prefix.value} - Clé: {key[:50]}..."
                if tenant_id:
                    log_msg += f" - Tenant: {tenant_id}"
                log_msg += f" - Params: {serializable_params}"
                logger.info(log_msg)
            else:
                # Supprime tout le prefix (ou pour un tenant spécifique si présent)
                if tenant_id:
                    pattern = f"{settings.app_redis_prefixe}:{prefix.value}:*tenant_id*{tenant_id}*"
                    await redis_cache.invalidate_pattern(pattern)
                    logger.info(f"🗑️ [CACHE INVALIDATE] {prefix.value} - Pattern tenant: {pattern}")
                else:
                    pattern = f"{settings.app_redis_prefixe}:{prefix.value}:*"
                    await redis_cache.invalidate_pattern(pattern)
                    logger.info(f"🗑️ [CACHE INVALIDATE] {prefix.value} - Pattern: {pattern}")

            return result

        return wrapper

    return decorator



def cacheable(
    prefix: CachePrefix,
    expire: Optional[int] = 60  # expiration par défaut
):
    """
    Décorateur qui met en cache automatique la sortie d'un use case ou service.
    Extrait automatiquement le tenant_id depuis current_user si présent.

    Usage:
        @cacheable(prefix=CachePrefix.CLIENTS)
        async def get_clients(page, limit, filters):
            ...

        # Multi-tenant: tenant_id est extrait automatiquement de current_user
        @cacheable(prefix=CachePrefix.PRODUCT_LIST, expire=300)
        async def list_products(current_user: CurrentUser, category: str, ...):
            # Cache isolé par tenant automatiquement
            ...
    """

    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            # - 1: Récupérer les noms & valeurs réels des paramètres
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            params = dict(bound.arguments)
           
            # - 2: Extraire tenant_id depuis current_user si présent
            tenant_id = None
            for param_name, param_value in params.items():
                if param_name == 'current_user' and hasattr(param_value, 'tenant_id'):
                    tenant_id = param_value.tenant_id
                    break

            # - 3: Filtrer les paramètres sérialisables (exclure les objets complexes et dépendances)
            serializable_params = {}
            for key, value in params.items():
                # Ignorer les dépendances injectées (repositories, services, etc.)
                if key.endswith('_case'):
                    continue

                # Ignorer current_user (on garde seulement tenant_id)
                if key == 'current_user':
                    continue

                # Garder seulement les types primitifs et collections simples
                if isinstance(value, (str, int, float, bool, type(None), list, BaseModel, dict, tuple)):
                    serializable_params[key] = value
                    if hasattr(value, 'model_dump'):  # Pydantic v2
                        for k, v in value.model_dump(mode="json").items():
                            serializable_params[k] = v
                        serializable_params.pop(key)
              
           
            # - 4: Ajouter tenant_id aux params si présent
            if tenant_id:
                serializable_params['tenant_id'] = tenant_id

            # - 5: Générer un hash de paramètres
            params_json = json.dumps(serializable_params, sort_keys=True, ensure_ascii=False)
           
            params_hash = redis_cache._generate_filter_hash({"params": params_json})
            
            # - 6: Construire la clé finale propre
            cache_key = f"{settings.app_redis_prefixe}:{prefix.value}:{params_hash}"
            logger.info(cache_key)
            # - 7: Vérifier si existe dans redis
            cached = await redis_cache.get(cache_key)
            if cached is not None:
                log_msg = f"🎯 [CACHE HIT] {prefix.value} - Clé: {cache_key[:50]}..."
                if tenant_id:
                    log_msg += f" - Tenant: {tenant_id}"
                log_msg += f" - Params: {serializable_params}"
                logger.info(log_msg)
                return cached

            log_msg = f"❌ [CACHE MISS] {prefix.value} - Exécution de la fonction"
            if tenant_id:
                log_msg += f" - Tenant: {tenant_id}"
            log_msg += f" - Params: {serializable_params}"

            # - 8: Exécuter la fonction réelle
            result = await func(*args, **kwargs)
            
            
            # - 9: Stocker en cache
            # Convertir les objets Pydantic en dict pour Redis
            cache_value = result
            if hasattr(result, 'model_dump'):  # Pydantic v2
                cache_value = result.model_dump(mode="json")
            elif hasattr(result, 'dict'):  # Pydantic v1
                cache_value = result.dict()
                
            
            logger.info(cache_value)

            await redis_cache.set(cache_key, cache_value, expire)
            log_msg = f"💾 [CACHE SET] {prefix.value} - Données mises en cache (expire: {expire}s)"
            if tenant_id:
                log_msg += f" - Tenant: {tenant_id}"
            logger.info(log_msg)
            return result

        return wrapper

    return decorator
