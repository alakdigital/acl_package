"""
Implémentation du cache avec Redis.
"""

import json
from typing import Any, Optional

import redis.asyncio as redis

from alak_acl.shared.cache.base import CacheBackend
from alak_acl.shared.exceptions import CacheConnectionError
from alak_acl.shared.logging import logger


class RedisCache(CacheBackend):
    """
    Implémentation du cache avec Redis asynchrone.

    Attributes:
        url: URL de connexion Redis
        default_ttl: TTL par défaut en secondes
        client: Client Redis
    """

    def __init__(self, url: str, default_ttl: int = 300):
        """
        Initialise le cache Redis.

        Args:
            url: URL de connexion (ex: redis://localhost:6379/0)
            default_ttl: TTL par défaut en secondes
        """
        self.url = url
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """
        Établit la connexion à Redis.

        Raises:
            CacheConnectionError: Si la connexion échoue
        """
        try:
            logger.info("Connexion à Redis...")
            self._client = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test de la connexion
            await self._client.ping()
            logger.info("Connexion Redis établie avec succès")

        except Exception as e:
            logger.error(f"Erreur de connexion Redis: {e}")
            raise CacheConnectionError(f"Impossible de se connecter à Redis: {e}")

    async def disconnect(self) -> None:
        """Ferme la connexion Redis."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Connexion Redis fermée")

    async def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache.

        Args:
            key: Clé de la valeur

        Returns:
            Valeur désérialisée ou None
        """
        if not self._client:
            return None

        try:
            value = await self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Erreur de lecture cache pour {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Stocke une valeur dans le cache.

        Args:
            key: Clé de la valeur
            value: Valeur à stocker (sera sérialisée en JSON)
            ttl: Durée de vie en secondes
        """
        if not self._client:
            return

        try:
            serialized = json.dumps(value)
            await self._client.set(
                key,
                serialized,
                ex=ttl or self.default_ttl,
            )
        except Exception as e:
            logger.warning(f"Erreur d'écriture cache pour {key}: {e}")

    async def delete(self, key: str) -> bool:
        """
        Supprime une valeur du cache.

        Args:
            key: Clé de la valeur

        Returns:
            True si supprimée
        """
        if not self._client:
            return False

        try:
            result = await self._client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Erreur de suppression cache pour {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe.

        Args:
            key: Clé à vérifier

        Returns:
            True si existe
        """
        if not self._client:
            return False

        try:
            return await self._client.exists(key) > 0
        except Exception:
            return False

    async def clear(self) -> None:
        """Vide tout le cache."""
        if not self._client:
            return

        try:
            await self._client.flushdb()
            logger.info("Cache Redis vidé")
        except Exception as e:
            logger.warning(f"Erreur lors du vidage du cache: {e}")

    async def is_connected(self) -> bool:
        """Vérifie si Redis est connecté."""
        if not self._client:
            return False

        try:
            await self._client.ping()
            return True
        except Exception:
            return False

    @property
    def backend_type(self) -> str:
        """Retourne 'redis'."""
        return "redis"

    async def set_hash(self, key: str, mapping: dict, ttl: Optional[int] = None) -> None:
        """
        Stocke un hash dans Redis.

        Args:
            key: Clé du hash
            mapping: Dictionnaire à stocker
            ttl: Durée de vie en secondes
        """
        if not self._client:
            return

        try:
            await self._client.hset(key, mapping=mapping)
            if ttl:
                await self._client.expire(key, ttl)
        except Exception as e:
            logger.warning(f"Erreur d'écriture hash pour {key}: {e}")

    async def get_hash(self, key: str) -> Optional[dict]:
        """
        Récupère un hash de Redis.

        Args:
            key: Clé du hash

        Returns:
            Dictionnaire ou None
        """
        if not self._client:
            return None

        try:
            return await self._client.hgetall(key)
        except Exception as e:
            logger.warning(f"Erreur de lecture hash pour {key}: {e}")
            return None
