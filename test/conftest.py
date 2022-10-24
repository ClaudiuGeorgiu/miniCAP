#!/usr/bin/env python3

import os

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from minicap.api import get_session
from minicap.database import Base
from minicap.main import app

SQLITE_TEST_DATABASE_URL = "sqlite+aiosqlite:///" + os.path.abspath(
    os.path.join(os.path.dirname(__file__), "captcha.test.db")
)

engine = create_async_engine(SQLITE_TEST_DATABASE_URL)
async_test_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def get_app() -> FastAPI:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with async_test_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield app


@pytest_asyncio.fixture
async def ac_client(get_app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=get_app, base_url="http://test") as client:
        yield client
