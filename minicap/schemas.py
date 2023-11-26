#!/usr/bin/env python3

from pydantic import BaseModel, Field


class CaptchaValidationRequest(BaseModel):
    id: str = Field(..., examples=["bca4cfaa-11a3-4577-8dc6-986d283012a8"])
    text: str = Field(..., examples=["8tRTu5"])


class CaptchaValidationResponse(BaseModel):
    status: int = Field(..., examples=[200])
    message: str = Field(..., examples=["CAPTCHA validated successfully"])
