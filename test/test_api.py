#!/usr/bin/env python3

from fastapi.testclient import TestClient

from minicap.main import app

client = TestClient(app)


class TestApi(object):
    def test_get_generate(self):
        response = client.get("/api/captcha/generate/")
        assert response.status_code == 200
        assert response.json() == {"msg": "TODO: generate CAPTCHA"}

    def test_post_validate(self):
        response = client.post("/api/captcha/validate/")
        assert response.status_code == 200
        assert response.json() == {"msg": "TODO: validate CAPTCHA"}
