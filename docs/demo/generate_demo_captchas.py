#!/usr/bin/env python3

import os
import re

from minicap.captcha import Captcha


def main():
    readme_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "README.md")
    )

    with open(readme_path, "r", encoding="utf-8") as readme_file:
        readme_content = readme_file.read()

    bg_noise = [False, True]
    fg_noise = [False, True]
    dark_theme = [False, True]

    for th in dark_theme:
        for bg in bg_noise:
            for fg in fg_noise:
                captcha = Captcha(
                    add_background_noise=bg,
                    add_foreground_noise=fg,
                    use_dark_theme=th,
                )

                img_name = (
                    f"{'dark' if th else 'light'}"
                    f"{'_bg' if bg else ''}"
                    f"{'_fg' if fg else ''}"
                    f".png"
                )

                img_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "img", img_name)
                )

                captcha.image.save(img_path, format="png", compress_level=3)

                readme_content = re.sub(
                    rf"({img_name}\)\s*)<br/>.+?<br/>",
                    rf"\1<br/>**{captcha.text}**<br/>",
                    readme_content,
                )

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)


if __name__ == "__main__":
    main()
