#!/usr/bin/env python3

import random

import pytest

from minicap.captcha import Captcha

random.seed(21)


class TestCaptcha:
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

    @pytest.mark.parametrize("add_background_noise", [True, False])
    @pytest.mark.parametrize("add_foreground_noise", [True, False])
    @pytest.mark.parametrize("use_dark_theme", [True, False])
    def test_theme_combinations(
        self, add_background_noise, add_foreground_noise, use_dark_theme
    ):
        captcha = Captcha(
            add_background_noise=add_background_noise,
            add_foreground_noise=add_foreground_noise,
            use_dark_theme=use_dark_theme,
        )

        if use_dark_theme:
            assert all(
                x < y for x, y in zip(captcha._get_fill_color(), (100, 100, 100))
            )
        else:
            assert all(
                x > y for x, y in zip(captcha._get_fill_color(), (100, 100, 100))
            )
