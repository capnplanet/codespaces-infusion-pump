from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base

from app.core import database
from app.core.security import get_current_user
from app.core.settings import APISettings, get_settings
from app.main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class TestSettings(APISettings):
    database_url: str = TEST_DATABASE_URL
    jwt_secret_key: str = "secret"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def override_settings() -> Generator[None, None, None]:
    database.get_engine.cache_clear()  # type: ignore[attr-defined]

    def _get_settings() -> APISettings:
        return TestSettings()

    app.dependency_overrides[get_settings] = _get_settings
    app.dependency_overrides[get_current_user] = lambda: {"sub": "tester"}
    yield
    app.dependency_overrides.pop(get_settings, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def session_factory(engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    database._engine = engine  # type: ignore[attr-defined]
    database._session_factory = session_factory  # type: ignore[attr-defined]
    yield session_factory
    database._session_factory = None  # type: ignore[attr-defined]
    database._engine = None  # type: ignore[attr-defined]


@pytest.fixture()
async def db_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
