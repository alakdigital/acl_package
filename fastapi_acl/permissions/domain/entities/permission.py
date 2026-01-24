"""
Entité Permission.

Représente une permission sous forme resource:action.
Supporte les wildcards pour les permissions globales.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


def generate_id() -> str:
    """Génère un ID unique sous forme de string UUID."""
    return str(uuid4())


@dataclass
class Permission:
    """
    Entité Permission du domaine.

    Une permission définit un droit d'accès sous forme resource:action.

    Attributes:
        id: Identifiant unique
        resource: Ressource concernée (ex: "posts", "users", "comments")
        action: Action autorisée (ex: "read", "create", "update", "delete", "*")
        name: Nom complet généré (resource:action)
        display_name: Nom d'affichage lisible
        description: Description de la permission
        is_active: Permission active ou non
        is_system: Permission système (non supprimable)
        category: Catégorie pour regroupement (ex: "Content", "Admin", "User")
        created_at: Date de création
        updated_at: Date de mise à jour

    Example:
        ```python
        # Permission simple
        perm = Permission(
            resource="posts",
            action="create",
            display_name="Créer des articles",
            description="Permet de créer de nouveaux articles",
            category="Content",
        )
        print(perm.name)  # "posts:create"

        # Permission wildcard
        admin_perm = Permission(
            resource="*",
            action="*",
            display_name="Super Admin",
            description="Tous les droits",
        )
        print(admin_perm.name)  # "*:*"

        # Vérification
        perm.matches("posts:create")  # True
        admin_perm.matches("posts:create")  # True (wildcard)
        ```
    """

    resource: str
    action: str
    id: str = field(default_factory=generate_id)
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_system: bool = False
    category: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Valide les données après initialisation."""
        if not self.resource:
            raise ValueError("resource ne peut pas être vide")
        if not self.action:
            raise ValueError("action ne peut pas être vide")

        # Normaliser en minuscules
        self.resource = self.resource.lower().strip()
        self.action = self.action.lower().strip()

        # Générer display_name si non fourni
        if not self.display_name:
            self.display_name = f"{self.resource.title()} - {self.action.title()}"

    @property
    def name(self) -> str:
        """
        Retourne le nom complet de la permission (resource:action).

        Returns:
            Nom au format "resource:action"
        """
        return f"{self.resource}:{self.action}"

    def matches(self, permission_name: str) -> bool:
        """
        Vérifie si cette permission correspond à un nom donné.

        Supporte les wildcards:
        - "*:*" correspond à tout
        - "posts:*" correspond à toutes les actions sur posts
        - "*:read" correspond à read sur toutes les ressources

        Args:
            permission_name: Nom de permission à vérifier (format "resource:action")

        Returns:
            True si la permission correspond
        """
        if ":" not in permission_name:
            return False

        target_resource, target_action = permission_name.split(":", 1)

        # Wildcard total
        if self.resource == "*" and self.action == "*":
            return True

        # Wildcard sur la ressource
        if self.resource == "*":
            return self.action == target_action or self.action == "*"

        # Wildcard sur l'action
        if self.action == "*":
            return self.resource == target_resource

        # Correspondance exacte
        return self.resource == target_resource and self.action == target_action

    @classmethod
    def from_name(
        cls,
        name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> "Permission":
        """
        Crée une permission depuis un nom au format "resource:action".

        Args:
            name: Nom au format "resource:action"
            display_name: Nom d'affichage (optionnel)
            description: Description (optionnel)
            category: Catégorie (optionnel)

        Returns:
            Nouvelle instance Permission

        Raises:
            ValueError: Si le format est invalide
        """
        if ":" not in name:
            raise ValueError(f"Format invalide: {name}. Attendu: 'resource:action'")

        resource, action = name.split(":", 1)
        return cls(
            resource=resource,
            action=action,
            display_name=display_name,
            description=description,
            category=category,
        )

    def to_dict(self) -> dict:
        """
        Convertit l'entité en dictionnaire.

        Returns:
            Dictionnaire représentant la permission
        """
        return {
            "id": self.id,
            "resource": self.resource,
            "action": self.action,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __eq__(self, other) -> bool:
        """Deux permissions sont égales si elles ont le même nom."""
        if isinstance(other, Permission):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        """Hash basé sur le nom de la permission."""
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Permission(name='{self.name}', category='{self.category}')"
