#!/usr/bin/env python3
"""Render Slides-format section files to 1920x1080 PNGs. usage: render_slides.py SLIDES_DIR BLOBS_JSON LOGOS_DIR OUT_DIR [ids...]"""
import json, re, subprocess, sys, html as H
from pathlib import Path
sd, logos, out = Path(sys.argv[1]), Path(sys.argv[3]).resolve(), Path(sys.argv[4])
blobs = json.loads(Path(sys.argv[2]).read_text()) if Path(sys.argv[2]).exists() else {}
out.mkdir(parents=True, exist_ok=True)
# Geist and Geist Mono (SIL Open Font License). A local copy of the font CSS with
# embedded files is used when present (offline renders); otherwise Google Fonts.
_local = [p for p in (Path(__file__).parent / "fonts.css", Path.home() / ".cache" / "deck-craft" / "fonts.css") if p.exists()]
FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap">'
fonts = _local[0].read_text() if _local else ""
CH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ids = sys.argv[5:] or sorted(p.stem for p in sd.glob("*.html"))
for sid in ids:
    h = (sd / f"{sid}.html").read_text()
    h = re.sub(r"<aside>.*?</aside>", "", h, flags=re.S)
    h = re.sub(r"/_blob/([0-9a-f]{32})", lambda m: f"file://{logos / blobs.get(m.group(1), 'missing')}", h)
    h = re.sub(r'<x-embed style="([^"]*)">(.*?)</x-embed>', lambda m: '<iframe style="' + m.group(1) + ';border:0" srcdoc="' + H.escape(m.group(2), quote=True) + '"></iframe>', h, flags=re.S)
    h = h.replace('style="', 'style="position:relative; width:1920px; height:1080px; overflow:hidden; box-sizing:border-box; ', 1)
    page = f"<!doctype html><html><head><meta charset=utf-8>{'' if fonts else FONT_LINK}<style>{fonts} html,body{{margin:0;padding:0}} *{{box-sizing:border-box}} p,h1,h2,h3,ul,ol{{margin:0}} table{{border-collapse:collapse}} th,td{{padding:10px 16px;border-bottom:1px solid #E3E6EA;text-align:left;vertical-align:top}} section > *:not([style*='position:absolute']){{position:relative}}</style></head><body>{h}</body></html>"
    f = out / f"{sid}.html"; f.write_text(page)
    subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1920,1080", "--virtual-time-budget=4000", f"--screenshot={out / (sid + '.png')}", f"file://{f.resolve()}"], capture_output=True)
print("rendered", len(ids))
