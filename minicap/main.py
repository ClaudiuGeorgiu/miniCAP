#!/usr/bin/env python3

import logging

import uvicorn
from fastapi import FastAPI

from minicap.api import api_router

# Logging configuration.
logging.basicConfig(
    format="%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=logging.INFO,
)

app = FastAPI()

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, log_config=None, host="0.0.0.0")
