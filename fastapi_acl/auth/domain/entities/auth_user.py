"""
Entité AuthUser - Représente un utilisateur authentifiable.

Cette entité supporte l'extension via des champs personnalisés
que le développeur peut définir selon ses besoins.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


def generate_id() -> str:
    """Génère un ID unique sous forme de string UUID."""
    return str(uuid4())


@dataclass
class AuthUser:
    """
    Entité métier représentant un utilisateur authentifiable.

    Cette entité est indépendante de la base de données et contient
    uniquement la logique métier liée à l'authentification.

    Le champ `extra_fields` permet au développeur d'ajouter des
    attributs personnalisés qui seront persistés en base de données.

    Attributes:
        id: Identifiant unique de l'utilisateur (string UUID)
        username: Nom d'utilisateur unique
        email: Adresse email unique
        hashed_password: Mot de passe hashé (bcrypt)
        is_active: Compte actif ou désactivé
        is_verified: Email vérifié
        is_superuser: Utilisateur administrateur
        created_at: Date de création
        updated_at: Date de dernière mise à jour
        last_login: Date de dernière connexion
        extra_fields: Champs personnalisés définis par le développeur

    Example:
        ```python
        user = AuthUser(
            username="john",
            email="john@example.com",
            hashed_password="...",
            extra_fields={
                "phone": "+33612345678",
                "company": "Acme Inc",
                "department": "Engineering",
            }
        )
        # Accès aux champs personnalisés
        print(user.get_extra("phone"))  # +33612345678
        user.set_extra("title", "Senior Developer")
        ```
    """

    username: str
    email: str
    hashed_password: str
    id: str = field(default_factory=generate_id)
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)

    def verify_password(self, plain_password: str, password_hasher) -> bool:
        """
        Vérifie si le mot de passe fourni correspond au hash.

        Args:
            plain_password: Mot de passe en clair
            password_hasher: Service de hashage (IPasswordHasher)

        Returns:
            True si le mot de passe est correct
        """
        return password_hasher.verify(plain_password, self.hashed_password)

    def is_authenticated(self) -> bool:
        """
        Vérifie si l'utilisateur peut s'authentifier.

        Un utilisateur peut s'authentifier s'il est actif.

        Returns:
            True si l'utilisateur peut s'authentifier
        """
        return self.is_active

    def can_access(self) -> bool:
        """
        Vérifie si l'utilisateur a accès à l'application.

        Un utilisateur a accès s'il est actif et vérifié.

        Returns:
            True si l'utilisateur a accès
        """
        return self.is_active and self.is_verified

    def update_last_login(self) -> None:
        """Met à jour la date de dernière connexion."""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Active le compte utilisateur."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Désactive le compte utilisateur."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def verify_email(self) -> None:
        """Marque l'email comme vérifié."""
        self.is_verified = True
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

    def remove_extra(self, key: str) -> Optional[Any]:
        """
        Supprime un champ personnalisé.

        Args:
            key: Nom du champ

        Returns:
            Valeur supprimée ou None
        """
        return self.extra_fields.pop(key, None)

    def has_extra(self, key: str) -> bool:
        """
        Vérifie si un champ personnalisé existe.

        Args:
            key: Nom du champ

        Returns:
            True si le champ existe
        """
        return key in self.extra_fields

    def to_dict(self, include_extra: bool = True) -> dict:
        """
        Convertit l'entité en dictionnaire.

        Args:
            include_extra: Inclure les champs personnalisés

        Returns:
            Dictionnaire représentant l'utilisateur
        """
        result = {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
        if include_extra and self.extra_fields:
            result["extra_fields"] = self.extra_fields.copy()
        return result

    def __eq__(self, other: object) -> bool:
        """Compare deux utilisateurs par leur ID."""
        if not isinstance(other, AuthUser):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id)
