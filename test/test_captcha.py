#!/usr/bin/env python3

import random

import pytest

from minicap.captcha import Captcha

random.seed(21)


class TestCaptcha(object):
    def test_valid_default(self):
        captcha = Captcha()
        assert captcha.text == "Zba4Hf"
        assert captcha.image.size == (600, 200)

    def test_invalid_size(self):
        with pytest.raises(ValueError) as e:
            Captcha(width=-1, height=-1)
        assert "Invalid width/height" in str(e.value)

    @pytest.mark.parametrize("width", [100, 200, 500, 1000])
    @pytest.mark.parametrize("height", [100, 200, 500, 1000])
    def test_valid_sizes(self, width, height):
        captcha = Captcha(text=f"{width}x{height}", width=width, height=height)
        assert captcha.image.size == (width, height)
