#!/usr/bin/env python3

import os
from datetime import datetime

from sqlalchemy import select, Column, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLITE_DATABASE_URL = "sqlite+aiosqlite:///" + os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, "captcha.db")
)

engine = create_async_engine(SQLITE_DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


async def get_generated_captcha(session: AsyncSession, captcha_id: str):
    return await session.scalar(
        select(GeneratedCaptcha).where(GeneratedCaptcha.id == captcha_id)
    )


async def add_captcha_to_db(session: AsyncSession, captcha_id: str, captcha_text: str):
    new_captcha = GeneratedCaptcha(id=captcha_id, text=captcha_text)
    session.add(new_captcha)
    await session.commit()
    await session.refresh(new_captcha)
    return new_captcha


class GeneratedCaptcha(Base):
    __tablename__ = "generated_captcha"

    id = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
