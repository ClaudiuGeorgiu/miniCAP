#!/usr/bin/env python3

import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from minicap.api import get_session
from minicap.database import Base, GeneratedCaptcha
from minicap.main import app

SQLITE_TEST_DATABASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "captcha.test.db")
)


@pytest_asyncio.fixture
async def get_app():
    engine = create_async_engine(
        "sqlite+aiosqlite:///" + SQLITE_TEST_DATABASE_PATH, poolclass=NullPool
    )
    async_test_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            insert(GeneratedCaptcha).values(
                id="valid-captcha-id", text="valid-captcha-solution"
            )
        )

    async def override_get_session():
        async with async_test_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield app

    os.remove(SQLITE_TEST_DATABASE_PATH)


@pytest_asyncio.fixture
async def ac_client(get_app):
    async with AsyncClient(
        transport=ASGITransport(app=get_app), base_url="http://test"
    ) as client:
        yield client
