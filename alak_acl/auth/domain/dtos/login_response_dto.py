"""
DTO pour la réponse de connexion avec roles et permissions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class RoleDTO:
    """
    Data Transfer Object pour un rôle.

    Attributes:
        id: Identifiant unique du rôle
        name: Nom du rôle
        display_name: Nom d'affichage
        permissions: Liste des permissions du rôle
    """

    id: str
    name: str
    display_name: Optional[str] = None
    permissions: List[str] = field(default_factory=list)


@dataclass
class UserDTO:
    """
    Data Transfer Object pour les informations utilisateur.

    Attributes:
        id: Identifiant unique
        username: Nom d'utilisateur
        email: Adresse email
        is_active: Compte actif
        is_verified: Email vérifié
        is_superuser: Administrateur
        created_at: Date de création
        last_login: Dernière connexion
    """

    id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


@dataclass
class LoginResponseDTO:
    """
    Data Transfer Object pour la réponse de connexion.

    Inclut les tokens, les informations utilisateur, les rôles et permissions.

    Attributes:
        access_token: Token d'accès JWT
        refresh_token: Token de rafraîchissement JWT
        token_type: Type de token (Bearer)
        expires_in: Durée de validité en secondes
        user: Informations utilisateur
        roles: Liste des rôles de l'utilisateur
        permissions: Liste des permissions uniques de l'utilisateur
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    user: Optional[UserDTO] = None
    roles: List[RoleDTO] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
