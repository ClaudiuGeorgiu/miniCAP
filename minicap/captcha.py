#!/usr/bin/env python3

import os
import random
import string

from PIL import Image, ImageDraw, ImageFilter, ImageFont


class Captcha:
    def __init__(self, text: str = None, width: int = 600, height: int = 200):
        self._text = text
        if not self._text:
            # If no input text is provided, generate a random string of 6 characters.
            # Some similar letters have been removed intentionally (e.g., 0 and O).
            self._text = "".join(
                random.choices(
                    "123456789abcdefghkmnpqrstuwxyzACDEFGHJKLMNPRSTUWXYZ", k=6
                )
            )

        if width <= 0 or height <= 0:
            raise ValueError("Invalid width/height")

        self._width = width
        self._height = height

        self._base_font_size = self._width // (len(self._text) + 2)

        self._font_path = os.path.join(
            os.path.dirname(__file__), "font", "JetBrainsMono.ttf"
        )
        self._padding = 5
        self._background_color = self._get_random_light_color()

        self._captcha_img = self._generate()

    @property
    def text(self) -> str:
        return self._text

    @property
    def image(self) -> Image:
        return self._captcha_img

    @staticmethod
    def _get_random_light_color() -> tuple[int, int, int]:
        return (
            random.randint(192, 255),
            random.randint(192, 255),
            random.randint(192, 255),
        )

    @staticmethod
    def _get_random_dark_color() -> tuple[int, int, int]:
        return random.randint(0, 96), random.randint(0, 96), random.randint(0, 96)

    def _draw_letter(self, letter: str) -> Image:
        # Use a different (random) font size every time this method is called.
        letter_font = ImageFont.truetype(
            self._font_path,
            size=random.randint(self._base_font_size, 2 * self._base_font_size),
        )
        stroke_width = random.randint(
            self._base_font_size // 16, self._base_font_size // 8
        )

        # Used only to get the bounding box of the letter.
        tmp_draw = ImageDraw.Draw(Image.new("RGBA", (self._padding, self._padding)))
        _, _, w, h = tmp_draw.textbbox(
            (self._padding, self._padding),
            letter,
            font=letter_font,
            stroke_width=stroke_width,
        )

        letter_img = Image.new("RGBA", (w, h))

        ImageDraw.Draw(letter_img).text(
            (self._padding, self._padding),
            letter,
            font=letter_font,
            fill=self._background_color,
            stroke_fill=self._get_random_dark_color(),
            stroke_width=stroke_width,
        )

        letter_img = letter_img.crop(letter_img.getbbox())

        letter_img = letter_img.rotate(
            random.randint(-40, 40), Image.Resampling.BICUBIC, expand=True
        )

        return letter_img

    def _add_background_noise(self, input_img: Image) -> Image:
        output_img = input_img.copy()

        y_block_size = (output_img.size[1] - 2 * self._padding) // 4

        try:
            x_block_size = (output_img.size[0] - 2 * self._padding) // (
                (output_img.size[0] // y_block_size) - 4
            )
        except ZeroDivisionError:
            # Can happen if the input image has similar width and height.
            x_block_size = output_img.size[0] - 2 * self._padding

        font_size = int(0.75 * y_block_size)

        # Draw random small letters all over the image.
        for y in range(self._padding, output_img.size[1] - y_block_size, y_block_size):
            for x in range(
                self._padding, output_img.size[0] - x_block_size, x_block_size
            ):
                tmp_font = ImageFont.truetype(
                    self._font_path, size=random.randint(font_size // 2, font_size)
                )
                color = self._get_random_dark_color()

                letter_img = Image.new("RGBA", (2 * tmp_font.size, 2 * tmp_font.size))
                ImageDraw.Draw(letter_img).text(
                    (1, 1),
                    random.choice(string.digits + string.ascii_letters),
                    font=tmp_font,
                    fill=color,
                    stroke_fill=color,
                    stroke_width=random.randint(0, 2),
                )

                letter_img = letter_img.crop(letter_img.getbbox())

                letter_img = letter_img.rotate(
                    random.randint(-60, 60), Image.Resampling.BICUBIC, expand=True
                )

                output_img.paste(
                    letter_img,
                    (
                        x
                        + ((x_block_size - font_size) // 2)
                        + random.randint(-x_block_size // 3, x_block_size // 3),
                        y
                        + ((y_block_size - font_size) // 2)
                        + random.randint(-y_block_size // 3, y_block_size // 3),
                    ),
                    letter_img,
                )

        return output_img

    def _add_foreground_noise(self, input_img: Image) -> Image:
        output_img = input_img.copy()
        draw = ImageDraw.Draw(output_img)

        block_size = (output_img.size[1] - 2 * self._padding) // 10

        # Draw random dots all over the image.
        for y in range(self._padding, output_img.size[1] - block_size, block_size):
            for x in range(self._padding, output_img.size[0] - block_size, block_size):
                r = random.randint(block_size // 10, block_size // 4)
                x_offset = random.randint(-block_size, block_size)
                y_offset = random.randint(-block_size, block_size)
                draw.ellipse(
                    (
                        x + block_size / 2 - r / 2 + x_offset,
                        y + block_size / 2 - r / 2 + y_offset,
                        x + block_size / 2 + r / 2 + x_offset,
                        y + block_size / 2 + r / 2 + y_offset,
                    ),
                    fill=self._get_random_dark_color(),
                )

        # Draw random lines (from left to right).
        y_range = output_img.size[1] // 3
        for _ in range(2):
            points = []
            for x in range(
                block_size,
                output_img.size[0] - block_size,
                output_img.size[0] // 5,
            ):
                points.append(
                    (x, output_img.size[1] // 2 + random.randint(-y_range, y_range))
                )
            points.append(
                (
                    output_img.size[0] - self._padding,
                    output_img.size[1] // 2 + random.randint(-y_range, y_range),
                )
            )

            draw.line(
                points,
                joint="curve",
                fill=self._get_random_dark_color(),
                width=random.randint(
                    self._base_font_size // 25, self._base_font_size // 15
                ),
            )

        return output_img

    def _generate(self) -> Image:
        letters = [self._draw_letter(letter) for letter in self.text]

        # Calculate the position where to place all the letters in the image, starting
        # from left side.
        x = [self._padding]
        y = []
        for position, letter_img in enumerate(letters):
            # Add a small random vertical offset to each letter.
            y.append(random.randint(self._padding, letter_img.size[1] // 2))
            # Add a small random horizontal offset between letters.
            x.append(
                x[-1]
                + letter_img.size[0]
                + (
                    random.randint(-letter_img.size[0] // 3, letter_img.size[0] // 5)
                    if position < len(letters) - 1
                    else self._padding
                )
            )

        # Use the tallest letter to calculate text height.
        text_height = 2 * self._padding + max(
            map(
                lambda item: item[0] + item[1],
                zip(y, map(lambda letter: letter.size[1], letters)),
            )
        )

        # Set width and height so that all the content will fit correctly.

        ratio = self._width / self._height

        tmp_width = self._width
        tmp_height = self._height

        if text_height > self._height:
            tmp_width += int((text_height - self._height) * ratio)
            tmp_height = text_height

        if x[-1] > tmp_width:
            tmp_height += int((x[-1] - tmp_width) / ratio)
            tmp_width = x[-1]

        w_factor = (tmp_width - x[-1]) // 2
        h_factor = (tmp_height - text_height) // 2

        # Prepare a CAPTCHA image of the right size to fit all the letters.
        captcha_img = Image.new("RGBA", (tmp_width, tmp_height), self._background_color)

        captcha_img = self._add_background_noise(captcha_img)

        # Add all the letters to the image.
        for position, letter_img in enumerate(letters):
            captcha_img.paste(
                letter_img, (x[position] + w_factor, y[position] + h_factor), letter_img
            )

        captcha_img = self._add_foreground_noise(captcha_img)

        captcha_img = captcha_img.filter(ImageFilter.SMOOTH)

        captcha_img.thumbnail((self._width, self._height), Image.Resampling.LANCZOS)

        return captcha_img
