"""
Fixtures pytest pour les tests.
"""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from fastapi_acl import ACLManager, ACLConfig
from fastapi_acl.auth.domain.entities.auth_user import AuthUser
from fastapi_acl.auth.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Crée un event loop pour les tests async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def password_hasher() -> BcryptPasswordHasher:
    """Fixture pour le password hasher."""
    return BcryptPasswordHasher(rounds=4)  # Moins de rounds pour les tests


@pytest.fixture
def test_config() -> ACLConfig:
    """Configuration de test avec cache mémoire."""
    return ACLConfig(
        database_type="postgresql",
        postgresql_uri="postgresql+asyncpg://test:test@localhost:5432/test_acl",
        enable_cache=True,
        cache_backend="memory",
        jwt_secret_key="test-secret-key-for-testing-minimum-32-chars",
        jwt_access_token_expire_minutes=5,
        enable_api_routes=True,
        enable_auth_feature=True,
        log_level="DEBUG",
    )


@pytest.fixture
def test_user(password_hasher: BcryptPasswordHasher) -> AuthUser:
    """Fixture pour un utilisateur de test."""
    return AuthUser(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password=password_hasher.hash("testpassword123"),
        is_active=True,
        is_verified=True,
    )


@pytest.fixture
def test_admin(password_hasher: BcryptPasswordHasher) -> AuthUser:
    """Fixture pour un admin de test."""
    return AuthUser(
        id=uuid4(),
        username="admin",
        email="admin@example.com",
        hashed_password=password_hasher.hash("adminpassword123"),
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )


@pytest.fixture
def app() -> FastAPI:
    """Crée une application FastAPI de test."""
    return FastAPI(title="Test App")
