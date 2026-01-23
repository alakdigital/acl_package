"""
Tests unitaires pour les services Auth.
"""

import pytest
from uuid import uuid4

from fastapi_acl import ACLConfig
from fastapi_acl.auth.infrastructure.services.jwt_token_service import JWTTokenService
from fastapi_acl.auth.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from fastapi_acl.shared.exceptions import InvalidTokenError, TokenExpiredError


class TestBcryptPasswordHasher:
    """Tests pour BcryptPasswordHasher."""

    def test_hash_password(self, password_hasher):
        """Test hashage d'un mot de passe."""
        password = "mypassword123"
        hashed = password_hasher.hash(password)

        assert hashed != password
        assert hashed.startswith("$2")  # bcrypt hash

    def test_verify_correct_password(self, password_hasher):
        """Test vérification mot de passe correct."""
        password = "mypassword123"
        hashed = password_hasher.hash(password)

        assert password_hasher.verify(password, hashed) is True

    def test_verify_wrong_password(self, password_hasher):
        """Test vérification mot de passe incorrect."""
        hashed = password_hasher.hash("mypassword123")

        assert password_hasher.verify("wrongpassword", hashed) is False

    def test_hash_is_unique(self, password_hasher):
        """Test que chaque hash est unique."""
        password = "mypassword123"
        hash1 = password_hasher.hash(password)
        hash2 = password_hasher.hash(password)

        assert hash1 != hash2  # Salt différent

    def test_needs_rehash(self, password_hasher):
        """Test needs_rehash avec un hash récent."""
        hashed = password_hasher.hash("mypassword123")

        # Hash récent = pas besoin de rehash
        assert password_hasher.needs_rehash(hashed) is False


class TestJWTTokenService:
    """Tests pour JWTTokenService."""

    @pytest.fixture
    def token_service(self, test_config):
        """Fixture pour le service de tokens."""
        return JWTTokenService(test_config)

    def test_create_access_token(self, token_service):
        """Test création access token."""
        user_id = uuid4()
        token = token_service.create_access_token(
            user_id=user_id,
            username="testuser",
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, token_service):
        """Test création refresh token."""
        user_id = uuid4()
        token = token_service.create_refresh_token(
            user_id=user_id,
            username="testuser",
        )

        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self, token_service):
        """Test décodage token valide."""
        user_id = uuid4()
        token = token_service.create_access_token(
            user_id=user_id,
            username="testuser",
            extra_data={"email": "test@example.com"},
        )

        payload = token_service.decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["username"] == "testuser"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_decode_invalid_token(self, token_service):
        """Test décodage token invalide."""
        with pytest.raises(InvalidTokenError):
            token_service.decode_token("invalid.token.here")

    def test_verify_valid_token(self, token_service):
        """Test vérification token valide."""
        token = token_service.create_access_token(
            user_id=uuid4(),
            username="testuser",
        )

        assert token_service.verify_token(token) is True

    def test_verify_invalid_token(self, token_service):
        """Test vérification token invalide."""
        assert token_service.verify_token("invalid") is False

    def test_get_user_id_from_token(self, token_service):
        """Test extraction user_id."""
        user_id = uuid4()
        token = token_service.create_access_token(
            user_id=user_id,
            username="testuser",
        )

        extracted_id = token_service.get_user_id_from_token(token)

        assert extracted_id == user_id

    def test_is_refresh_token(self, token_service):
        """Test détection refresh token."""
        user_id = uuid4()

        access_token = token_service.create_access_token(
            user_id=user_id,
            username="testuser",
        )
        refresh_token = token_service.create_refresh_token(
            user_id=user_id,
            username="testuser",
        )

        assert token_service.is_refresh_token(access_token) is False
        assert token_service.is_refresh_token(refresh_token) is True

    def test_token_expiry(self, token_service):
        """Test durée de validité."""
        expiry = token_service.get_token_expiry()

        assert expiry == 5 * 60  # 5 minutes en config test
