"""
Tests unitaires pour les Use Cases Auth.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi_acl.auth.domain.entities.auth_user import AuthUser
from fastapi_acl.auth.domain.dtos.login_dto import LoginDTO
from fastapi_acl.auth.domain.dtos.register_dto import RegisterDTO
from fastapi_acl.auth.application.usecases.login_usecase import LoginUseCase
from fastapi_acl.auth.application.usecases.register_usecase import RegisterUseCase
from fastapi_acl.auth.application.usecases.refresh_token_usecase import RefreshTokenUseCase
from fastapi_acl.shared.exceptions import (
    InvalidCredentialsError,
    UserNotActiveError,
    UserAlreadyExistsError,
    InvalidTokenError,
)


class TestLoginUseCase:
    """Tests pour LoginUseCase."""

    @pytest.fixture
    def mock_repository(self):
        """Mock du repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_token_service(self):
        """Mock du service de tokens."""
        mock = MagicMock()
        mock.create_access_token.return_value = "access_token"
        mock.create_refresh_token.return_value = "refresh_token"
        return mock

    @pytest.fixture
    def mock_password_hasher(self):
        """Mock du password hasher."""
        mock = MagicMock()
        mock.verify.return_value = True
        return mock

    @pytest.fixture
    def login_usecase(self, mock_repository, mock_token_service, mock_password_hasher):
        """Fixture pour le use case."""
        return LoginUseCase(
            auth_repository=mock_repository,
            token_service=mock_token_service,
            password_hasher=mock_password_hasher,
        )

    @pytest.mark.asyncio
    async def test_login_success(self, login_usecase, mock_repository, test_user):
        """Test connexion réussie."""
        mock_repository.get_by_username.return_value = test_user
        mock_repository.update_user.return_value = test_user

        dto = LoginDTO(username="testuser", password="testpassword123")
        result = await login_usecase.execute(dto)

        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        assert result.token_type == "Bearer"

    @pytest.mark.asyncio
    async def test_login_by_email(self, login_usecase, mock_repository, test_user):
        """Test connexion par email."""
        mock_repository.get_by_username.return_value = None
        mock_repository.get_by_email.return_value = test_user
        mock_repository.update_user.return_value = test_user

        dto = LoginDTO(username="test@example.com", password="testpassword123")
        result = await login_usecase.execute(dto)

        assert result.access_token is not None

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, login_usecase, mock_repository):
        """Test connexion utilisateur non trouvé."""
        mock_repository.get_by_username.return_value = None
        mock_repository.get_by_email.return_value = None

        dto = LoginDTO(username="unknown", password="password")

        with pytest.raises(InvalidCredentialsError):
            await login_usecase.execute(dto)

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, login_usecase, mock_repository, mock_password_hasher, test_user
    ):
        """Test connexion mot de passe incorrect."""
        mock_repository.get_by_username.return_value = test_user
        mock_password_hasher.verify.return_value = False

        dto = LoginDTO(username="testuser", password="wrongpassword")

        with pytest.raises(InvalidCredentialsError):
            await login_usecase.execute(dto)

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self, login_usecase, mock_repository, test_user
    ):
        """Test connexion compte désactivé."""
        test_user.is_active = False
        mock_repository.get_by_username.return_value = test_user

        dto = LoginDTO(username="testuser", password="testpassword123")

        with pytest.raises(UserNotActiveError):
            await login_usecase.execute(dto)


class TestRegisterUseCase:
    """Tests pour RegisterUseCase."""

    @pytest.fixture
    def mock_repository(self):
        """Mock du repository."""
        mock = AsyncMock()
        mock.username_exists.return_value = False
        mock.email_exists.return_value = False
        return mock

    @pytest.fixture
    def mock_password_hasher(self):
        """Mock du password hasher."""
        mock = MagicMock()
        mock.hash.return_value = "hashed_password"
        return mock

    @pytest.fixture
    def register_usecase(self, mock_repository, mock_password_hasher):
        """Fixture pour le use case."""
        return RegisterUseCase(
            auth_repository=mock_repository,
            password_hasher=mock_password_hasher,
        )

    @pytest.mark.asyncio
    async def test_register_success(self, register_usecase, mock_repository):
        """Test inscription réussie."""
        mock_repository.create_user.return_value = AuthUser(
            username="newuser",
            email="new@example.com",
            hashed_password="hashed_password",
        )

        dto = RegisterDTO(
            username="newuser",
            email="new@example.com",
            password="password123",
        )
        result = await register_usecase.execute(dto)

        assert result.username == "newuser"
        assert result.email == "new@example.com"
        mock_repository.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_username_exists(self, register_usecase, mock_repository):
        """Test inscription username existant."""
        mock_repository.username_exists.return_value = True

        dto = RegisterDTO(
            username="existinguser",
            email="new@example.com",
            password="password123",
        )

        with pytest.raises(UserAlreadyExistsError):
            await register_usecase.execute(dto)

    @pytest.mark.asyncio
    async def test_register_email_exists(self, register_usecase, mock_repository):
        """Test inscription email existant."""
        mock_repository.email_exists.return_value = True

        dto = RegisterDTO(
            username="newuser",
            email="existing@example.com",
            password="password123",
        )

        with pytest.raises(UserAlreadyExistsError):
            await register_usecase.execute(dto)


class TestRefreshTokenUseCase:
    """Tests pour RefreshTokenUseCase."""

    @pytest.fixture
    def mock_repository(self):
        """Mock du repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_token_service(self):
        """Mock du service de tokens."""
        mock = MagicMock()
        mock.is_refresh_token.return_value = True
        mock.decode_token.return_value = {"sub": str(uuid4())}
        mock.get_user_id_from_token.return_value = uuid4()
        mock.create_access_token.return_value = "new_access_token"
        return mock

    @pytest.fixture
    def refresh_usecase(self, mock_repository, mock_token_service):
        """Fixture pour le use case."""
        return RefreshTokenUseCase(
            auth_repository=mock_repository,
            token_service=mock_token_service,
        )

    @pytest.mark.asyncio
    async def test_refresh_success(
        self, refresh_usecase, mock_repository, mock_token_service, test_user
    ):
        """Test rafraîchissement réussi."""
        mock_token_service.get_user_id_from_token.return_value = test_user.id
        mock_repository.get_by_id.return_value = test_user

        result = await refresh_usecase.execute("valid_refresh_token")

        assert result.access_token == "new_access_token"
        assert result.token_type == "Bearer"

    @pytest.mark.asyncio
    async def test_refresh_not_refresh_token(
        self, refresh_usecase, mock_token_service
    ):
        """Test avec un access token au lieu d'un refresh token."""
        mock_token_service.is_refresh_token.return_value = False

        with pytest.raises(InvalidTokenError):
            await refresh_usecase.execute("access_token")

    @pytest.mark.asyncio
    async def test_refresh_inactive_user(
        self, refresh_usecase, mock_repository, mock_token_service, test_user
    ):
        """Test rafraîchissement pour utilisateur inactif."""
        test_user.is_active = False
        mock_token_service.get_user_id_from_token.return_value = test_user.id
        mock_repository.get_by_id.return_value = test_user

        with pytest.raises(UserNotActiveError):
            await refresh_usecase.execute("valid_refresh_token")
