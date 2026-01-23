"""
Implémentation du cache en mémoire (fallback).
"""

import asyncio
from typing import Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


from .base import CacheBackend
from ..logging import logger


@dataclass
class CacheEntry:
    """Entrée de cache avec expiration."""
    value: Any
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class MemoryCache(CacheBackend):
    """
    Implémentation du cache en mémoire.

    Utilisé comme fallback quand Redis n'est pas disponible.
    Attention: Ce cache n'est pas partagé entre les workers!

    Attributes:
        default_ttl: TTL par défaut en secondes
        cache: Dictionnaire de stockage
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialise le cache mémoire.

        Args:
            default_ttl: TTL par défaut en secondes
        """
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry] = {}
        self._connected = False
        self._cleanup_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Initialise le cache mémoire."""
        logger.info("Initialisation du cache mémoire (fallback)")
        self._connected = True
        # Démarre la tâche de nettoyage périodique
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def disconnect(self) -> None:
        """Ferme le cache mémoire."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self._cache.clear()
        self._connected = False
        logger.info("Cache mémoire fermé")

    async def _periodic_cleanup(self) -> None:
        """Nettoie périodiquement les entrées expirées."""
        while True:
            try:
                await asyncio.sleep(60)  # Nettoyage toutes les 60 secondes
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Erreur lors du nettoyage du cache: {e}")

    async def _cleanup_expired(self) -> None:
        """Supprime les entrées expirées."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Nettoyage cache: {len(expired_keys)} entrées expirées supprimées")

    async def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache.

        Args:
            key: Clé de la valeur

        Returns:
            Valeur ou None si non trouvée/expirée
        """
        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry.is_expired():
            del self._cache[key]
            return None

        return entry.value

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
            value: Valeur à stocker
            ttl: Durée de vie en secondes
        """
        expires_at = None
        if ttl or self.default_ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)

        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    async def delete(self, key: str) -> bool:
        """
        Supprime une valeur du cache.

        Args:
            key: Clé de la valeur

        Returns:
            True si supprimée
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe et n'est pas expirée.

        Args:
            key: Clé à vérifier

        Returns:
            True si existe et valide
        """
        entry = self._cache.get(key)
        if entry is None:
            return False

        if entry.is_expired():
            del self._cache[key]
            return False

        return True

    async def clear(self) -> None:
        """Vide tout le cache."""
        self._cache.clear()
        logger.info("Cache mémoire vidé")

    async def is_connected(self) -> bool:
        """Vérifie si le cache est initialisé."""
        return self._connected

    @property
    def backend_type(self) -> str:
        """Retourne 'memory'."""
        return "memory"

    @property
    def size(self) -> int:
        """Retourne le nombre d'entrées dans le cache."""
        return len(self._cache)
