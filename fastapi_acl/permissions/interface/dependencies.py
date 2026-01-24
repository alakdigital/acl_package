"""
Dépendances FastAPI pour la feature Permissions.

Fournit l'injection de dépendances pour les repositories et services.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status

from ..application.interface.permission_repository import IPermissionRepository
from ...shared.exceptions import ConfigurationError


# Variable globale pour stocker le repository (configurée au démarrage)
_permission_repository: Optional[IPermissionRepository] = None


def set_permission_dependencies(
    permission_repository: IPermissionRepository,
) -> None:
    """
    Configure les dépendances pour les permissions.

    Cette fonction doit être appelée au démarrage de l'application
    par l'ACLManager.

    Args:
        permission_repository: Repository des permissions
    """
    global _permission_repository
    _permission_repository = permission_repository


def get_permission_repository() -> IPermissionRepository:
    """
    Dépendance FastAPI pour obtenir le repository des permissions.

    Returns:
        Repository des permissions

    Raises:
        HTTPException: Si le repository n'est pas configuré
    """
    if _permission_repository is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission repository non configuré. "
                   "Vérifiez que enable_permissions_feature=True",
        )
    return _permission_repository
