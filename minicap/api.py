#!/usr/bin/env python3

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/api")


@api_router.get("/captcha/generate/")
async def generate_captcha():
    return {"msg": "TODO: generate CAPTCHA"}


@api_router.post("/captcha/validate/")
async def validate_captcha():
    return {"msg": "TODO: validate CAPTCHA"}
