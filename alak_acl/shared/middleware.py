# from functools import wraps
# import logging
# from typing import Any, Callable, Optional
# import inspect
# import json

# from pydantic import BaseModel
# from app.caches.cache_manager import CacheManager, CachePrefix

# logger = logging.getLogger(__name__)

# redis_cache = CacheManager()
# setting = Settings()

# # ============================================================
# # Utils
# # ============================================================

# def extract_account_id(value: Any) -> Optional[str]:
#     """
#     Extrait account_no depuis :
#     - modèle Pydantic
#     - dictionnaire
#     - objet classique
#     - None
#     """
#     if value is None:
#         return None

#     # Cas modèle Pydantic (v1 & v2)
#     if isinstance(value, BaseModel):
#         # Pydantic v2
#         if hasattr(value, "model_dump"):
#             return value.model_dump().get("account_no")
       

#     # Cas dictionnaire
#     if isinstance(value, dict):
#         return value.get("account_no")

#     #  Cas objet classique
#     return getattr(value, "account_no", None)


# def serialize_params(params: dict) -> dict:
#     """
#     Nettoie et sérialise les paramètres pour le cache
#     """
#     serializable = {}

#     for key, value in params.items():
#         # Ignorer dépendances et paramètres techniques
#         if key.endswith("_case"):
#             continue
#         if key in ("current_user", "pressing"):
#             continue
#         if key.startswith("_"):
#             continue
#         if key == "search" and value is None:
#             continue

#         # Pydantic v2
#         if hasattr(value, "model_dump"):
#             serializable.update(value.model_dump(mode="json"))
#             continue

#         # Types simples
#         if isinstance(value, (str, int, float, bool, type(None))):
#             serializable[key] = value
#             continue

#         # List / Dict / Tuple sécurisés
#         if isinstance(value, (list, dict, tuple)):
#             serializable[key] = json.loads(
#                 json.dumps(value, default=str)
#             )

#     return serializable


# def build_cache_key(prefix: CachePrefix, params: dict, id_pressing: Optional[str]) -> str:
#     """
#     Génère une clé Redis STRICTEMENT cohérente partout
#     """
#     params_json = json.dumps(params, sort_keys=True, ensure_ascii=False)
#     params_hash = redis_cache._generate_filter_hash({"params": params_json})

#     if id_pressing:
#         return (
#             f"{setting.APP_REDIS_PREFIXE}:"
#             f"{prefix.value}:Pressing:{id_pressing}:{params_hash}"
#         )

#     return f"{setting.APP_REDIS_PREFIXE}:{prefix.value}:{params_hash}"


# # ============================================================
# # Invalidate cache decorator
# # ============================================================

# def invalidate_cache(prefix: CachePrefix, param_keys: Optional[list[str]] = None):

#     def decorator(func: Callable):

#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             result = await func(*args, **kwargs)

#             sig = inspect.signature(func)
#             bound = sig.bind_partial(*args, **kwargs)
#             bound.apply_defaults()
#             func_params = dict(bound.arguments)

#             # --- Extract id_pressing
#             id_pressing = None
#             for value in func_params.values():
#                 id_pressing = extract_id_pressing(value)
#                 if id_pressing:
#                     break

#             # --- Invalidate specific key
#             if param_keys:
#                 filtered = {
#                     k: v for k, v in func_params.items()
#                     if k in param_keys
#                 }

#                 serializable = serialize_params(filtered)

#                 if id_pressing:
#                     serializable["id_pressing"] = id_pressing

#                 cache_key = build_cache_key(prefix, serializable, id_pressing)

#                 await redis_cache._scan_and_delete(cache_key)

#                 logger.info(
#                     f"🗑️ [CACHE INVALIDATE] {prefix.value} "
#                     f"- Key: {cache_key[:80]}..."
#                 )

#             # --- Invalidate whole prefix
#             else:
#                 if id_pressing:
#                     pattern = (
#                         f"{setting.APP_REDIS_PREFIXE}:"
#                         f"{prefix.value}:Pressing:{id_pressing}:*"
#                     )
#                 else:
#                     pattern = (
#                         f"{setting.APP_REDIS_PREFIXE}:"
#                         f"{prefix.value}:*"
#                     )

#                 await redis_cache._scan_and_delete(pattern)

#                 logger.info(
#                     f"🗑️ [CACHE INVALIDATE] {prefix.value} "
#                     f"- Pattern: {pattern}"
#                 )

#             return result

#         return wrapper

#     return decorator


# # ============================================================
# # Cacheable decorator
# # ============================================================

# def cacheable(
#     prefix: CachePrefix,
#     expire: Optional[int] = 60
# ):

#     def decorator(func: Callable):

#         @wraps(func)
#         async def wrapper(*args, **kwargs):

#             sig = inspect.signature(func)
#             bound = sig.bind_partial(*args, **kwargs)
#             bound.apply_defaults()
#             params = dict(bound.arguments)

#             # --- Extract id_pressing
#             id_pressing = None
#             for value in params.values():
#                 id_pressing = extract_id_pressing(value)
#                 if id_pressing:
#                     break

#             # --- Serialize params
#             serializable = serialize_params(params)

#             if id_pressing:
#                 serializable["id_pressing"] = id_pressing

#             # --- Build key
#             cache_key = build_cache_key(prefix, serializable, id_pressing)
            
#             # --- Cache HIT
#             cached = await redis_cache.get_cache(cache_key)
#             if cached is not None:
#                 logger.info(
#                     f"🎯 [CACHE HIT] {prefix.value} "
#                     f"- Key: {cache_key[:80]}..."
#                 )
#                 return cached

#             logger.info(
#                 f"❌ [CACHE MISS] {prefix.value} "
#                 f"- Params: {serializable}"
#             )

#             # --- Execute function
#             result = await func(*args, **kwargs)

#             # --- Normalize cache value
#             cache_value = result
#             if hasattr(result, "model_dump"):
#                 cache_value = result.model_dump(mode="json")
#             elif hasattr(result, "dict"):
#                 cache_value = result.dict()

#             await redis_cache.set_cache_with_tracking(
#                 cache_key,
#                 cache_value,
#                 expire
#             )

#             logger.info(
#                 f"💾 [CACHE SET] {prefix.value} "
#                 f"- Expire: {expire}s"
#             )

#             return result

#         return wrapper

#     return decorator
