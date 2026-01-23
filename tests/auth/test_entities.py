"""
Tests unitaires pour les entités Auth.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from fastapi_acl.auth.domain.entities.auth_user import AuthUser
from fastapi_acl.auth.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher


class TestAuthUser:
    """Tests pour l'entité AuthUser."""

    def test_create_user(self):
        """Test création d'un utilisateur."""
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_superuser is False
        assert user.id is not None

    def test_user_with_custom_id(self):
        """Test création avec ID personnalisé."""
        custom_id = uuid4()
        user = AuthUser(
            id=custom_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
        )

        assert user.id == custom_id

    def test_is_authenticated(self):
        """Test méthode is_authenticated."""
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=True,
        )

        assert user.is_authenticated() is True

        user.is_active = False
        assert user.is_authenticated() is False

    def test_can_access(self):
        """Test méthode can_access."""
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=True,
            is_verified=False,
        )

        assert user.can_access() is False

        user.is_verified = True
        assert user.can_access() is True

        user.is_active = False
        assert user.can_access() is False

    def test_activate_deactivate(self):
        """Test activation/désactivation."""
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=False,
        )

        assert user.is_active is False

        user.activate()
        assert user.is_active is True

        user.deactivate()
        assert user.is_active is False

    def test_verify_email(self):
        """Test vérification email."""
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_verified=False,
        )

        assert user.is_verified is False

        user.verify_email()
        assert user.is_verified is True

    def test_update_last_login(self):
        """Test mise à jour last_login."""
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
        )

        assert user.last_login is None

        before = datetime.utcnow()
        user.update_last_login()

        assert user.last_login is not None
        assert user.last_login >= before

    def test_to_dict(self):
        """Test conversion en dictionnaire."""
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
        )

        data = user.to_dict()

        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data  # Ne doit pas exposer le hash
        assert "id" in data

    def test_equality(self):
        """Test égalité entre utilisateurs."""
        id1 = uuid4()
        user1 = AuthUser(
            id=id1,
            username="user1",
            email="user1@example.com",
            hashed_password="hash1",
        )
        user2 = AuthUser(
            id=id1,
            username="user2",
            email="user2@example.com",
            hashed_password="hash2",
        )

        assert user1 == user2  # Même ID = égal

        user3 = AuthUser(
            username="user3",
            email="user3@example.com",
            hashed_password="hash3",
        )

        assert user1 != user3  # IDs différents

    def test_verify_password(self, password_hasher):
        """Test vérification du mot de passe."""
        hashed = password_hasher.hash("mypassword")
        user = AuthUser(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed,
        )

        assert user.verify_password("mypassword", password_hasher) is True
        assert user.verify_password("wrongpassword", password_hasher) is False
