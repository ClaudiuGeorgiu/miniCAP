#!/usr/bin/env python3

import os
from datetime import datetime

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SQLITE_DATABASE_URL = "sqlite+aiosqlite:///" + os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, "captcha.db")
)

engine = create_async_engine(SQLITE_DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class GeneratedCaptcha(Base):
    __tablename__ = "generated_captcha"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(10), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)
    validation_counter: Mapped[int] = mapped_column(default=0)


async def get_generated_captcha(session: AsyncSession, captcha_id: str):
    return await session.scalar(
        select(GeneratedCaptcha).where(GeneratedCaptcha.id == captcha_id)
    )


async def add_captcha_to_db(session: AsyncSession, captcha_id: str, captcha_text: str):
    new_captcha = GeneratedCaptcha(id=captcha_id, text=captcha_text)
    session.add(new_captcha)
    await session.commit()
    return new_captcha


async def delete_captcha_from_db(session: AsyncSession, captcha: GeneratedCaptcha):
    await session.delete(captcha)
    await session.commit()


async def increment_captcha_validation_counter(
    session: AsyncSession, captcha: GeneratedCaptcha
):
    captcha.validation_counter += 1
    session.add(captcha)
    await session.commit()
