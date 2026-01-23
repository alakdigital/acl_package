"""
Tests unitaires pour les DTOs Auth.
"""

import pytest

from fastapi_acl.auth.domain.dtos.login_dto import LoginDTO
from fastapi_acl.auth.domain.dtos.register_dto import RegisterDTO
from fastapi_acl.auth.domain.dtos.token_dto import TokenDTO


class TestLoginDTO:
    """Tests pour LoginDTO."""

    def test_valid_login(self):
        """Test création d'un LoginDTO valide."""
        dto = LoginDTO(username="testuser", password="password123")

        assert dto.username == "testuser"
        assert dto.password == "password123"

    def test_empty_username(self):
        """Test avec username vide."""
        with pytest.raises(ValueError, match="nom d'utilisateur"):
            LoginDTO(username="", password="password123")

    def test_whitespace_username(self):
        """Test avec username espaces."""
        with pytest.raises(ValueError, match="nom d'utilisateur"):
            LoginDTO(username="   ", password="password123")

    def test_empty_password(self):
        """Test avec password vide."""
        with pytest.raises(ValueError, match="mot de passe"):
            LoginDTO(username="testuser", password="")

    def test_immutable(self):
        """Test que le DTO est immutable."""
        dto = LoginDTO(username="testuser", password="password123")

        with pytest.raises(AttributeError):
            dto.username = "newuser"


class TestRegisterDTO:
    """Tests pour RegisterDTO."""

    def test_valid_register(self):
        """Test création d'un RegisterDTO valide."""
        dto = RegisterDTO(
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        assert dto.username == "testuser"
        assert dto.email == "test@example.com"
        assert dto.password == "password123"

    def test_username_too_short(self):
        """Test username trop court."""
        with pytest.raises(ValueError, match="au moins 3 caractères"):
            RegisterDTO(
                username="ab",
                email="test@example.com",
                password="password123",
            )

    def test_username_too_long(self):
        """Test username trop long."""
        with pytest.raises(ValueError, match="50 caractères"):
            RegisterDTO(
                username="a" * 51,
                email="test@example.com",
                password="password123",
            )

    def test_username_invalid_chars(self):
        """Test username avec caractères invalides."""
        with pytest.raises(ValueError, match="lettres, chiffres"):
            RegisterDTO(
                username="test@user",
                email="test@example.com",
                password="password123",
            )

    def test_valid_username_chars(self):
        """Test username avec caractères valides."""
        dto = RegisterDTO(
            username="test_user-123",
            email="test@example.com",
            password="password123",
        )
        assert dto.username == "test_user-123"

    def test_invalid_email(self):
        """Test email invalide."""
        with pytest.raises(ValueError, match="email"):
            RegisterDTO(
                username="testuser",
                email="invalid-email",
                password="password123",
            )

    def test_password_too_short(self):
        """Test password trop court."""
        with pytest.raises(ValueError, match="8 caractères"):
            RegisterDTO(
                username="testuser",
                email="test@example.com",
                password="short",
            )

    def test_password_too_long(self):
        """Test password trop long."""
        with pytest.raises(ValueError, match="128 caractères"):
            RegisterDTO(
                username="testuser",
                email="test@example.com",
                password="a" * 129,
            )


class TestTokenDTO:
    """Tests pour TokenDTO."""

    def test_minimal_token(self):
        """Test création avec access token uniquement."""
        dto = TokenDTO(access_token="test.token.here")

        assert dto.access_token == "test.token.here"
        assert dto.token_type == "Bearer"
        assert dto.refresh_token is None
        assert dto.expires_in is None

    def test_full_token(self):
        """Test création complète."""
        dto = TokenDTO(
            access_token="access.token",
            refresh_token="refresh.token",
            token_type="Bearer",
            expires_in=1800,
        )

        assert dto.access_token == "access.token"
        assert dto.refresh_token == "refresh.token"
        assert dto.expires_in == 1800

    def test_to_dict(self):
        """Test conversion en dictionnaire."""
        dto = TokenDTO(
            access_token="access.token",
            refresh_token="refresh.token",
            expires_in=1800,
        )

        data = dto.to_dict()

        assert data["access_token"] == "access.token"
        assert data["refresh_token"] == "refresh.token"
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 1800

    def test_to_dict_minimal(self):
        """Test conversion minimale."""
        dto = TokenDTO(access_token="access.token")

        data = dto.to_dict()

        assert "refresh_token" not in data
        assert "expires_in" not in data
