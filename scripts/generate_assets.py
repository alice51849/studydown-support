#!/usr/bin/env python3
"""Render deterministic Studydown web artwork without a generative image API."""

from __future__ import annotations

import pathlib
import shutil

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SOURCE = ROOT / "source"


def lerp(a: int, b: int, value: float) -> int:
    return round(a + (b - a) * value)


def vertical_gradient(size: tuple[int, int], top: tuple[int, ...], bottom: tuple[int, ...]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(height):
        amount = y / max(1, height - 1)
        colour = tuple(lerp(top[index], bottom[index], amount) for index in range(4))
        for x in range(width):
            pixels[x, y] = colour
    return image


def add_glow(image: Image.Image, centre: tuple[int, int], radius: int, colour: tuple[int, int, int, int]) -> None:
    layer = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(layer)
    x, y = centre
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colour)
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.58))
    image.alpha_composite(layer)


def render_icon(size: int = 1024) -> Image.Image:
    scale = size / 1024
    image = vertical_gradient(
        (size, size), (255, 248, 252, 255), (91, 141, 239, 255)
    )
    add_glow(image, (round(size * 0.78), round(size * 0.22)), round(size * 0.28), (242, 99, 160, 150))
    add_glow(image, (round(size * 0.23), round(size * 0.79)), round(size * 0.3), (155, 111, 227, 125))
    mask = Image.new("L", (size, size))
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=round(228 * scale), fill=255
    )
    image.putalpha(mask)
    draw = ImageDraw.Draw(image, "RGBA")
    centre = size // 2
    draw.ellipse(
        (round(164 * scale), round(164 * scale), round(860 * scale), round(860 * scale)),
        fill=(255, 255, 255, 78),
        outline=(255, 255, 255, 150),
        width=max(2, round(8 * scale)),
    )
    ring_box = (round(244 * scale), round(244 * scale), round(780 * scale), round(780 * scale))
    ring = Image.new("RGBA", image.size)
    ring_draw = ImageDraw.Draw(ring, "RGBA")
    colours = [(242, 99, 160, 255), (155, 111, 227, 255), (91, 141, 239, 255)]
    for degree in range(360):
        amount = degree / 359
        if amount < 0.5:
            local = amount * 2
            colour = tuple(lerp(colours[0][i], colours[1][i], local) for i in range(4))
        else:
            local = (amount - 0.5) * 2
            colour = tuple(lerp(colours[1][i], colours[2][i], local) for i in range(4))
        ring_draw.arc(
            ring_box,
            start=degree - 1,
            end=degree + 1,
            fill=colour,
            width=max(8, round(56 * scale)),
        )
    shadow = ring.filter(ImageFilter.GaussianBlur(round(18 * scale)))
    shadow.putalpha(shadow.getchannel("A").point(lambda value: value * 0.35))
    image.alpha_composite(shadow, (0, round(22 * scale)))
    image.alpha_composite(ring)
    phone_box = (round(370 * scale), round(326 * scale), round(654 * scale), round(716 * scale))
    phone_shadow = Image.new("RGBA", image.size)
    ImageDraw.Draw(phone_shadow).rounded_rectangle(
        tuple(value + round(20 * scale) for value in phone_box),
        radius=round(62 * scale),
        fill=(52, 28, 80, 90),
    )
    phone_shadow = phone_shadow.filter(ImageFilter.GaussianBlur(round(26 * scale)))
    image.alpha_composite(phone_shadow)
    draw.rounded_rectangle(phone_box, radius=round(62 * scale), fill=(255, 255, 255, 232), outline=(255, 255, 255, 255), width=max(2, round(8 * scale)))
    draw.rounded_rectangle((round(398 * scale), round(354 * scale), round(626 * scale), round(688 * scale)), radius=round(43 * scale), fill=(238, 233, 247, 255))
    draw.ellipse((round(416 * scale), round(375 * scale), round(460 * scale), round(419 * scale)), fill=(242, 99, 160, 255))
    draw.ellipse((round(430 * scale), round(389 * scale), round(446 * scale), round(405 * scale)), fill=(255, 255, 255, 180))
    width = max(5, round(18 * scale))
    draw.line((round(456 * scale), round(614 * scale), round(568 * scale), round(614 * scale)), fill=(155, 111, 227, 255), width=width)
    draw.line((centre, round(558 * scale), centre, round(670 * scale)), fill=(91, 141, 239, 255), width=width)
    return image


def font(size: int, rounded: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        pathlib.Path("/System/Library/Fonts/SFNSRounded.ttf") if rounded else pathlib.Path("/System/Library/Fonts/SFNS.ttf"),
        pathlib.Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        pathlib.Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def render_social() -> Image.Image:
    image = vertical_gradient((1200, 630), (255, 248, 252, 255), (238, 247, 255, 255))
    add_glow(image, (110, 80), 310, (242, 99, 160, 115))
    add_glow(image, (1100, 580), 330, (91, 141, 239, 105))
    icon = render_icon(480)
    image.alpha_composite(icon, (720, 76))
    draw = ImageDraw.Draw(image)
    draw.text((92, 205), "Studydown", font=font(86), fill=(36, 29, 50, 255))
    draw.text(
        (96, 315),
        "Face-down focus, clearly recorded.",
        font=font(34),
        fill=(98, 90, 115, 255),
    )
    draw.text(
        (96, 386),
        "WORK  •  LEARNING  •  DAILY LIFE",
        font=font(24),
        fill=(121, 95, 197, 255),
    )
    return image


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE / "site-icon.svg", ASSETS / "site-icon.svg")
    render_icon().resize((256, 256), Image.Resampling.LANCZOS).save(
        ASSETS / "site-icon.png", optimize=True
    )
    render_social().save(ASSETS / "social-card.png", optimize=True)
    print("Generated site-icon.png (256×256) and social-card.png (1200×630).")


if __name__ == "__main__":
    main()
