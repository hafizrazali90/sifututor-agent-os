#!/usr/bin/env python3
"""Build ican-uitm-deck.html from the template.

Usage (from anywhere): python3 docs/ican-uitm-partnership/build.py

1. Splices the embedded fonts through the doc-design build script
   (.claude/skills/doc-design/scripts/build.py), which also strips em dashes
   and checks tag balance.
2. Inlines the brand assets in ./assets as data URIs and the Malaysia map as
   inline SVG.
3. Writes the per-slide page counter into each slide's bottom bar.
"""
import base64
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
FONT_BUILD = REPO / ".claude" / "skills" / "doc-design" / "scripts" / "build.py"
TEMPLATE = HERE / "ican-uitm-deck.template.html"
INTERMEDIATE = HERE / ".ican-uitm-deck.fonts.html"
OUT = HERE / "ican-uitm-deck.html"
ASSETS = HERE / "assets"


def data_uri(name: str, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode((ASSETS / name).read_bytes()).decode()


def main() -> None:
    subprocess.run([sys.executable, str(FONT_BUILD), str(TEMPLATE), str(INTERMEDIATE)], check=True)
    html = INTERMEDIATE.read_text()
    INTERMEDIATE.unlink()

    html = html.replace("@@LOGO_SIFU@@", data_uri("sifututor-logo.png", "image/png"))
    html = html.replace("@@LOGO_NN@@", data_uri("nakngaji-logo.svg", "image/svg+xml"))
    html = html.replace("@@IMG_HUMAN@@", data_uri("human-learning.jpg", "image/jpeg"))
    html = html.replace("@@IMG_PARENT@@", data_uri("parent-coordination.jpg", "image/jpeg"))

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
    counter = iter(range(1, total + 1))
    html = re.sub(r'<span class="count"></span>', lambda _m: f'<span class="count">{next(counter)} / {total}</span>', html)

    leftover = re.findall(r"@@[A-Z_]+@@", html)
    assert not leftover, f"unspliced asset tokens: {leftover}"

    OUT.write_text(html)
    print(f"built {OUT.name}: {len(html)} bytes, {total} slides")


if __name__ == "__main__":
    main()
