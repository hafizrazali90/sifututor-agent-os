#!/usr/bin/env python3
"""Build a deck from slide modules. Run from the deck folder.

deck.py in the deck folder defines:
  TITLE    deck title
  FOOTER   footer text after the owner name
  OWNER    owner name shown bold in the footer (the client presenting, or Learnest Lab)
  ORDER    slide ids in order
  APPENDIX slide ids numbered A1, A2, ... (optional)
  NOPAGE   slide ids with no page number, e.g. cover and close (optional)
  SECTIONS {key: {"description": ..., "start": slide id}} (optional)
  MODULES  slide module names, each exposing SLIDES = [functions]
Optional tokens.py with expand(html) -> html replaces {{TOKENS}} with ledger values.

usage: build.py [--mod=name] [--render [ids...]]
"""
import importlib, json, subprocess, sys
from pathlib import Path

HERE = Path.cwd()
SKILL = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(SKILL))
import lib  # noqa: E402
cfg = importlib.import_module("deck")
lib.DECK["footer"], lib.DECK["owner"] = cfg.FOOTER, cfg.OWNER
expand = importlib.import_module("tokens").expand if (HERE / "tokens.py").exists() else (lambda h: h)

appendix, nopage = getattr(cfg, "APPENDIX", []), set(getattr(cfg, "NOPAGE", ["cover", "close"]))
n = 2
for sid in cfg.ORDER:
    if sid in nopage:
        continue
    if sid in appendix:
        lib.PG[sid] = f"A{appendix.index(sid) + 1}"
    else:
        lib.PG[sid] = f"{n:02d}"; n += 1

mods = [a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--mod=")] or cfg.MODULES
fns = {f.__name__: f for m in mods for f in importlib.import_module(m).SLIDES}
src, out = HERE / "src", HERE / "project" / "slides"
src.mkdir(exist_ok=True); out.mkdir(parents=True, exist_ok=True)
built = []
for sid in cfg.ORDER:
    if sid not in fns:
        continue
    html = fns[sid]()
    assert f'<section id="{sid}"' in html, f"{sid}: section id must match the function name"
    (src / f"{sid}.html").write_text(html)
    (out / f"{sid}.html").write_text(expand(html))
    built.append(sid)

if len(built) == len(cfg.ORDER):
    (HERE / "order.json").write_text(json.dumps(built))
    deck = {"v": 4, "lists": "css", "title": cfg.TITLE, "order": built,
            "sections": getattr(cfg, "SECTIONS", {}),
            "faces": {"geist": {"family": "Geist", "href": "https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap"},
                      "geist-mono": {"family": "Geist Mono", "href": "https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&display=swap"}},
            "designSystems": []}
    (HERE / "project" / "deck.json").write_text(json.dumps(deck, indent=1))
print(len(built), "slides:", " ".join(built))

if "--render" in sys.argv:
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or built
    subprocess.run([sys.executable, str(SKILL / "render_slides.py"), str(out), str(HERE / "blobs.json"), str(HERE / "logos"), str(HERE / "png")] + ids)
