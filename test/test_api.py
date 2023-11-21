#!/usr/bin/env python3

import datetime

import pytest
from fastapi import status
from httpx import AsyncClient

import minicap.api
from minicap.schemas import CaptchaValidationRequest


class TestApi:
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
            json=CaptchaValidationRequest(id="invalid", text="invalid").model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_validate_good_solution(self, ac_client: AsyncClient):
        request = CaptchaValidationRequest(
            id="valid-captcha-id", text="valid-captcha-solution"
        ).model_dump()

        response1 = await ac_client.post("/api/captcha/validate/", json=request)
        assert response1.status_code == status.HTTP_200_OK

        response2 = await ac_client.post("/api/captcha/validate/", json=request)
        assert response2.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_validate_bad_solution(self, ac_client: AsyncClient):
        request = CaptchaValidationRequest(
            id="valid-captcha-id", text="bad-captcha-solution"
        ).model_dump()

        for _ in range(0, 3):
            response = await ac_client.post("/api/captcha/validate/", json=request)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

        last_response = await ac_client.post("/api/captcha/validate/", json=request)
        assert last_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_validate_after_too_much_time(
        self, ac_client: AsyncClient, monkeypatch
    ):
        class MockDateTime(datetime.datetime):
            @classmethod
            def utcnow(cls):
                return datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

        monkeypatch.setattr(minicap.api, "datetime", MockDateTime)

        request = CaptchaValidationRequest(
            id="valid-captcha-id", text="valid-captcha-solution"
        ).model_dump()

        response = await ac_client.post("/api/captcha/validate/", json=request)
        assert response.status_code == status.HTTP_404_NOT_FOUND
