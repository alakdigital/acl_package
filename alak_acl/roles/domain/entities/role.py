"""
Entité Role - Représente un rôle dans le système.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


def generate_id() -> str:
    """Génère un ID unique sous forme de string UUID."""
    return str(uuid4())


@dataclass
class Role:
    """
    Entité métier représentant un rôle.

    Un rôle permet de regrouper des permissions et de les attribuer
    à des utilisateurs.

    Attributes:
        id: Identifiant unique du rôle (string)
        name: Nom unique du rôle (ex: "admin", "moderator")
        display_name: Nom d'affichage du rôle
        description: Description du rôle
        permissions: Liste des permissions associées
        is_active: Rôle actif ou non
        is_default: Rôle attribué par défaut aux nouveaux utilisateurs
        is_system: Rôle système (ne peut pas être supprimé)
        priority: Priorité du rôle (plus haute = plus importante)
        created_at: Date de création
        updated_at: Date de dernière mise à jour
        extra_fields: Champs personnalisés ajoutés par héritage du modèle

    Example:
        ```python
        role = Role(
            name="moderator",
            display_name="Modérateur",
            description="Peut modérer le contenu",
            permissions=["posts:read", "posts:update", "comments:delete"],
        )
        ```
    """

    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    id: str = field(default_factory=generate_id)
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    is_default: bool = False
    is_system: bool = False
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    extra_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialise display_name si non fourni."""
        if self.display_name is None:
            self.display_name = self.name.replace("_", " ").title()

    def has_permission(self, permission: str) -> bool:
        """
        Vérifie si le rôle a une permission spécifique.

        Args:
            permission: Nom de la permission à vérifier

        Returns:
            True si le rôle a la permission
        """
        # Support des wildcards
        if "*" in self.permissions:
            return True

        # Vérification exacte
        if permission in self.permissions:
            return True

        # Vérification hiérarchique (ex: "posts:*" couvre "posts:read")
        parts = permission.split(":")
        if len(parts) > 1:
            wildcard = f"{parts[0]}:*"
            if wildcard in self.permissions:
                return True

        return False

    def add_permission(self, permission: str) -> None:
        """
        Ajoute une permission au rôle.

        Args:
            permission: Permission à ajouter
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = datetime.utcnow()

    def remove_permission(self, permission: str) -> bool:
        """
        Retire une permission du rôle.

        Args:
            permission: Permission à retirer

        Returns:
            True si la permission a été retirée
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def set_permissions(self, permissions: List[str]) -> None:
        """
        Définit la liste complète des permissions.

        Args:
            permissions: Liste des permissions
        """
        self.permissions = list(permissions)
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Active le rôle."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Désactive le rôle."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def set_as_default(self) -> None:
        """Définit ce rôle comme rôle par défaut."""
        self.is_default = True
        self.updated_at = datetime.utcnow()

    def unset_as_default(self) -> None:
        """Retire ce rôle comme rôle par défaut."""
        self.is_default = False
        self.updated_at = datetime.utcnow()

    def get_extra(self, key: str, default: Any = None) -> Any:
        """
        Récupère un champ personnalisé.

        Args:
            key: Nom du champ
            default: Valeur par défaut si le champ n'existe pas

        Returns:
            Valeur du champ ou default
        """
        return self.extra_fields.get(key, default)

    def set_extra(self, key: str, value: Any) -> None:
        """
        Définit un champ personnalisé.

        Args:
            key: Nom du champ
            value: Valeur du champ
        """
        self.extra_fields[key] = value
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_extra: bool = True) -> dict:
        """
        Convertit l'entité en dictionnaire.

        Args:
            include_extra: Inclure les champs personnalisés

        Returns:
            Dictionnaire représentant le rôle
        """
        result = {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "permissions": self.permissions.copy(),
            "is_active": self.is_active,
            "is_default": self.is_default,
            "is_system": self.is_system,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_extra and self.extra_fields:
            result["extra_fields"] = self.extra_fields.copy()
        return result

    def __eq__(self, other: object) -> bool:
        """Compare deux rôles par leur ID."""
        if not isinstance(other, Role):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
