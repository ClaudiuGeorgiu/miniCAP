#!/usr/bin/env python3

import pytest
from fastapi import status
from httpx import AsyncClient

from minicap.schemas import CaptchaValidationRequest


class TestApi(object):
    @pytest.mark.asyncio
    async def test_generate_ok(self, ac_client: AsyncClient):
        response = await ac_client.post("/api/captcha/generate/")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("Content-Type") == "image/png"

    @pytest.mark.asyncio
    async def test_validate_invalid_request(self, ac_client: AsyncClient):
        response = await ac_client.post("/api/captcha/validate/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_validate_not_found(self, ac_client: AsyncClient):
        response = await ac_client.post(
            "/api/captcha/validate/",
            json=CaptchaValidationRequest(id="invalid", text="invalid").dict(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_validate_good_solution(self, ac_client: AsyncClient):
        response = await ac_client.post(
            "/api/captcha/validate/",
            json=CaptchaValidationRequest(
                id="valid-captcha-id", text="valid-captcha-solution"
            ).dict(),
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_validate_bad_solution(self, ac_client: AsyncClient):
        response = await ac_client.post(
            "/api/captcha/validate/",
            json=CaptchaValidationRequest(
                id="valid-captcha-id", text="bad-captcha-solution"
            ).dict(),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
