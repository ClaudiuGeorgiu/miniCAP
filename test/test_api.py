#!/usr/bin/env python3

from fastapi import status
from fastapi.testclient import TestClient

from minicap.main import app

client = TestClient(app)


class TestApi(object):
    def test_post_generate_ok(self):
        response = client.post("/api/captcha/generate/")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("Content-Type") == "image/png"

    def test_post_validate_invalid_request(self):
        response = client.post("/api/captcha/validate/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
