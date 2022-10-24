#!/usr/bin/env python3

import pytest
from fastapi import status
from httpx import AsyncClient

from minicap.schemas import CaptchaValidationRequest


class TestApi(object):
    @pytest.mark.asyncio
    async def test_post_generate_ok(self, ac_client: AsyncClient):
        response = await ac_client.post("/api/captcha/generate/")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("Content-Type") == "image/png"

    @pytest.mark.asyncio
    async def test_post_generate_ok_and_validate_error(self, ac_client: AsyncClient):
        response = await ac_client.post("/api/captcha/generate/")
        assert response.status_code == status.HTTP_200_OK

        captcha_id = response.headers.get("Captcha-Id")
        response = await ac_client.post(
            "/api/captcha/validate/",
            json=CaptchaValidationRequest(id=captcha_id, text="invalid").dict(),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_post_validate_invalid_request(self, ac_client: AsyncClient):
        response = await ac_client.post("/api/captcha/validate/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
