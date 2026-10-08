#!/usr/bin/env python3
"""Contact sheets: sheet.py OUT_PREFIX id1 id2 ... (2 columns, 960 wide each)."""
import sys
from pathlib import Path
from PIL import Image
HERE = Path.cwd()
pre = sys.argv[1]; ids = sys.argv[2:]
per = 4
for n in range(0, len(ids), per):
    chunk = ids[n:n+per]
    W, H = 960, 540
    im = Image.new("RGB", (W*2 + 30, (H+10) * ((len(chunk)+1)//2) + 10), "#888888")
    for i, sid in enumerate(chunk):
        p = Image.open(HERE / "png" / f"{sid}.png").convert("RGB").resize((W, H), Image.LANCZOS)
        im.paste(p, (10 + (i % 2) * (W+10), 10 + (i//2) * (H+10)))
    im.save(HERE / "png" / f"{pre}{n//per}.png")
    print(HERE / "png" / f"{pre}{n//per}.png")
