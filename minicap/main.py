#!/usr/bin/env python3

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from minicap.api import api_router
from minicap.database import Base, engine

logging.getLogger("aiosqlite").level = logging.WARNING
logging.getLogger("sqlalchemy").level = logging.WARNING

# Logging configuration.
logging.basicConfig(
    format="%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=logging.DEBUG,  # Set to INFO or ERROR in production.
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create database table(s) at startup.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Create FastAPI application.
app = FastAPI(
    title="miniCAP",
    description="A simple and minimal microservice for generating and "
    "validating CAPTCHA.",
    version="1.0.0",
    lifespan=lifespan,
)

# Needed if the API is used by a browser. Origins should be set to the allowed domains
# instead of wildcard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    expose_headers=["captcha_id"],
)

# Include API routes.
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, log_config=None, host="0.0.0.0")
