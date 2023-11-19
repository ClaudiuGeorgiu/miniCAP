#!/usr/bin/env python3

import io
import logging
import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from minicap.captcha import Captcha
from minicap.database import (
    async_session,
    add_captcha_to_db,
    delete_captcha_from_db,
    get_generated_captcha,
    increment_captcha_validation_counter,
)
from minicap.schemas import CaptchaValidationRequest, CaptchaValidationResponse

MAX_VALIDATION_REQUESTS = 3

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/api")


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@api_router.post(
    "/captcha/generate/",
    tags=["captcha"],
    description="Generate a new CAPTCHA",
    response_class=Response,
    responses={
        status.HTTP_200_OK: {
            "description": "CAPTCHA generated successfully",
            "content": {"image/png": {}},
        },
    },
)
async def generate_captcha(session: AsyncSession = Depends(get_session)):
    captcha = Captcha()
    captcha_bytes = io.BytesIO()

    captcha.image.save(captcha_bytes, format="png")
    captcha_bytes.seek(0)

    captcha_id = str(uuid.uuid4())

    await add_captcha_to_db(session, captcha_id, captcha.text)

    logger.debug(f"New CAPTCHA for string '{captcha.text}' with id {captcha_id}")

    return Response(
        media_type="image/png",
        content=captcha_bytes.getvalue(),
        headers={
            "Captcha-Id": captcha_id,
        },
    )


@api_router.post(
    "/captcha/validate/",
    tags=["captcha"],
    description="Validate a previously generated CAPTCHA",
    response_model=CaptchaValidationResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "CAPTCHA to validate not found",
            "model": CaptchaValidationResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "CAPTCHA to validate not found",
                    }
                }
            },
        },
        status.HTTP_200_OK: {
            "description": "CAPTCHA validated successfully",
            "model": CaptchaValidationResponse,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "CAPTCHA validation failed",
            "model": CaptchaValidationResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "CAPTCHA validation failed",
                    }
                }
            },
        },
    },
)
async def validate_captcha(
    response: Response,
    validation_request: CaptchaValidationRequest,
    session: AsyncSession = Depends(get_session),
):
    existing_captcha = await get_generated_captcha(session, validation_request.id)
    if not existing_captcha:
        response.status_code = status.HTTP_404_NOT_FOUND
        return CaptchaValidationResponse(
            status=response.status_code, message="CAPTCHA to validate not found"
        )
    if validation_request.text.lower() == existing_captcha.text.lower():
        # Make CAPTCHA validation case insensitive.
        await delete_captcha_from_db(session, existing_captcha)
        response.status_code = status.HTTP_200_OK
        return CaptchaValidationResponse(
            status=response.status_code, message="CAPTCHA validated successfully"
        )
    else:
        await increment_captcha_validation_counter(session, existing_captcha)
        if existing_captcha.validation_counter >= MAX_VALIDATION_REQUESTS:
            await delete_captcha_from_db(session, existing_captcha)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return CaptchaValidationResponse(
            status=response.status_code, message="CAPTCHA validation failed"
        )
