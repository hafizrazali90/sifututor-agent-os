#!/usr/bin/env python3
"""Rebuild ican-uitm-deck.html from the template.

Usage: python3 docs/ican-uitm-partnership/build.py

Self-contained: needs only Python 3 and the files in this folder. It splices the
embedded fonts from assets/fonts, inlines the brand assets as data URIs and the
Malaysia outline as inline SVG, writes each slide's page counter, and applies the
house rule that em dashes never appear in output.
"""
import base64
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "ican-uitm-deck.template.html"
OUT = HERE / "ican-uitm-deck.html"
ASSETS = HERE / "assets"
FONTS = ASSETS / "fonts"

FONT_TOKENS = {
    "{{ARCH700}}": "archivo-700.b64",
    "{{ARCH600}}": "archivo-600.b64",
    "{{PLEX400}}": "plex-400.b64",
    "{{PLEX600}}": "plex-600.b64",
    "{{PLEX700}}": "plex-700.b64",
}

IMAGES = {
    "@@LOGO_SIFU@@": ("sifututor-logo.png", "image/png"),
    "@@LOGO_NN@@": ("nakngaji-logo.svg", "image/svg+xml"),
    "@@IMG_HUMAN@@": ("human-learning.jpg", "image/jpeg"),
    "@@IMG_PARENT@@": ("parent-coordination.jpg", "image/jpeg"),
}


def main() -> int:
    html = TEMPLATE.read_text()

    # House rule: no em dashes anywhere in produced output.
    html = html.replace(" — ", ", ").replace("—", "-")

    for token, filename in FONT_TOKENS.items():
        html = html.replace(token, (FONTS / filename).read_text().strip())

    for token, (filename, mime) in IMAGES.items():
        encoded = base64.b64encode((ASSETS / filename).read_bytes()).decode()
        html = html.replace(token, f"data:{mime};base64,{encoded}")

    svg = (ASSETS / "malaysia-map.svg").read_text()
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg)
    svg = re.sub(
        r"<svg([^>]*)>",
        lambda m: "<svg" + re.sub(r'\s(width|height)="[^"]*"', "", m.group(1)) + ' aria-hidden="true">',
        svg,
        count=1,
    )
    html = html.replace("@@MAP_SVG@@", svg)

    total = html.count('<section class="slide')
    numbers = iter(range(1, total + 1))
    html = re.sub(
        r'<span class="count"></span>',
        lambda _m: f'<span class="count">{next(numbers)} / {total}</span>',
        html,
    )

    leftover = sorted(set(re.findall(r"@@[A-Z_]+@@|\{\{[A-Z0-9]+\}\}", html)))
    if leftover:
        print(f"error: unspliced tokens remain: {leftover}", file=sys.stderr)
        return 1

    OUT.write_text(html)
    print(f"built {OUT.name}: {len(html)} bytes, {total} slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
