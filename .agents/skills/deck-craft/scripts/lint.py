#!/usr/bin/env python3
"""Geometry lint for rendered slides. usage: lint.py [PNG_DIR] [ids...]
Loads png/<id>.html (written by render_slides.py) in headless Chrome and reports, as arithmetic:
OUT   text or box outside the 128px side margins or below y=968 (footer row starts at 984)
SPILL content taller or wider than the box that holds it (text running out of a card)
CLIP  a nowrap or overflow-hidden text cut off
OVER  two separate texts whose ink overlaps
SMALL text under 24px
EMPTY lowest content edge above y=880 (slide looks empty at the bottom)
HOLLOW a card more than 30% empty at the bottom (half-empty card)
"""
import json, re, subprocess, sys
from pathlib import Path
HERE = Path.cwd()
args = sys.argv[1:]
d = HERE / "png"
if args and Path(args[0]).is_dir():
    d = Path(args.pop(0))
ids = args or json.loads((HERE / "order.json").read_text())
CH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
JS = r"""
<script>
window.addEventListener('load', () => { setTimeout(() => {
const out = []; const sec = document.querySelector('section');
const R = e => e.getBoundingClientRect();
const txt = e => (e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 46);
const isFooter = e => { const r = R(e); return r.top >= 975; };
const all = [...sec.querySelectorAll('*')].filter(e => !e.closest('svg') || e.tagName === 'svg');
const leaves = [];
for (const e of all) {
  if (e.tagName === 'svg' || e.tagName === 'ASIDE') continue;
  const r = R(e); if (r.width === 0 || r.height === 0) continue;
  const cs = getComputedStyle(e);
  const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  if (own) {
    const fs = parseFloat(cs.fontSize); if (fs < 24) out.push(['SMALL', fs + 'px', txt(e)]);
    const rg = document.createRange(); rg.selectNodeContents(e);
    const lines = [...rg.getClientRects()].filter(q => q.width > 1 && q.height > 1);
    leaves.push({e, lines});
    if (!isFooter(e)) for (const q of lines) {
      if (q.left < 126 || q.right > 1794) { out.push(['OUT', 'x ' + Math.round(q.left) + ' to ' + Math.round(q.right), txt(e)]); break; }
      if (q.bottom > 968) { out.push(['OUT', 'bottom ' + Math.round(q.bottom), txt(e)]); break; }
    }
    if (e.scrollWidth > e.clientWidth + 2 && (cs.whiteSpace === 'nowrap' || cs.overflow === 'hidden')) out.push(['CLIP', 'needs ' + e.scrollWidth + ' has ' + e.clientWidth, txt(e)]);
    // text outside nearest visible box
    let a = e.parentElement;
    while (a && a !== sec) { const s = getComputedStyle(a); const boxed = (s.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(s.borderTopWidth) > 0);
      if (boxed) { const ar = R(a); for (const q of lines) { if (q.right > ar.right + 1 || q.bottom > ar.bottom + 1 || q.left < ar.left - 1 || q.top < ar.top - 1) { out.push(['SPILL', 'text leaves its box by ' + Math.round(Math.max(q.right - ar.right, q.bottom - ar.bottom, ar.left - q.left, ar.top - q.top)) + 'px', txt(e)]); break; } } break; }
      a = a.parentElement; }
  }
  if (!isFooter(e) && r.width < 1900 && (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.borderTopWidth) > 0)) {
    if (r.left < 126 || r.right > 1794) out.push(['OUT', 'box x ' + Math.round(r.left) + ' to ' + Math.round(r.right), txt(e)]);
    if (r.bottom > 968) out.push(['OUT', 'box bottom ' + Math.round(r.bottom), txt(e)]);
    if (e.scrollHeight > e.clientHeight + 3 && e.clientHeight > 0 && cs.display !== 'inline') out.push(['SPILL', 'box needs ' + e.scrollHeight + ' high, has ' + e.clientHeight, txt(e)]);
    if (e.scrollWidth > e.clientWidth + 3 && e.clientWidth > 0 && cs.display !== 'inline') out.push(['SPILL', 'box needs ' + e.scrollWidth + ' wide, has ' + e.clientWidth, txt(e)]);
    // HOLLOW: a card whose content fills too little of it (pure backdrops with no children are skipped)
    if (e.children.length && r.height > 140) {
      let cb = r.top;
      for (const c of e.querySelectorAll('*')) { const cr = R(c); if (cr.height && cr.width) cb = Math.max(cb, cr.bottom); }
      const pb = parseFloat(cs.paddingBottom) || 0;
      const empty = r.bottom - pb - cb;
      // skip backdrops that other elements are drawn over, and small grid cells (heat maps)
      const overlaid = leaves.some(L => !e.contains(L.e) && L.lines.some(q => q.top >= cb && q.bottom <= r.bottom && q.left >= r.left && q.right <= r.right));
      const overlaidBox = [...sec.querySelectorAll('div')].some(o => !e.contains(o) && !o.contains(e) && (() => { const orr = R(o); return orr.top >= cb - 2 && orr.bottom <= r.bottom + 2 && orr.left >= r.left - 2 && orr.right <= r.right + 2 && orr.height > 20; })());
      if (!overlaid && !overlaidBox && r.width >= 300 && empty > 90 && empty / r.height > 0.3) out.push(['HOLLOW', Math.round(empty) + 'px empty at the bottom of a ' + Math.round(r.height) + 'px box', txt(e)]);
    }
    // child boxes leaving the parent box
    for (const c of e.children) { const cr = R(c); if (cr.width && (cr.right > r.right + 2 || cr.bottom > r.bottom + 2)) { out.push(['SPILL', 'child leaves box by ' + Math.round(Math.max(cr.right - r.right, cr.bottom - r.bottom)) + 'px', txt(c)]); } }
  }
}
for (let i = 0; i < leaves.length; i++) for (let j = i + 1; j < leaves.length; j++) {
  const A = leaves[i], B = leaves[j]; if (A.e.contains(B.e) || B.e.contains(A.e)) continue;
  let hit = 0; for (const p of A.lines) for (const q of B.lines) { const w = Math.min(p.right, q.right) - Math.max(p.left, q.left), h = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top); if (w > 3 && h > 6) hit = Math.max(hit, w * h); }
  if (hit > 40) out.push(['OVER', Math.round(hit) + 'px2', txt(A.e) + ' <> ' + txt(B.e)]);
}
let low = 0; for (const e of all) { if (e.tagName === 'svg' || e === sec) continue; const r = R(e); if (r.height && r.width < 1900 && r.top < 975) low = Math.max(low, Math.min(r.bottom, 975)); }
if (low < 880 && sec.id !== 'cover' && sec.id !== 'close') out.push(['EMPTY', 'content ends at y=' + Math.round(low), '']);
out.push(['COUNT', sec.querySelectorAll('*').length + ' elements', '']);
const pre = document.createElement('pre'); pre.id = 'lintout'; pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}, 300); });
</script>
"""
total = 0
for sid in ids:
    f = d / f"{sid}.html"
    if not f.exists():
        print(f"{sid}: not rendered"); continue
    t = d / f"_lint_{sid}.html"
    t.write_text(f.read_text().replace("</body>", JS + "</body>"))
    r = subprocess.run([CH, "--headless=new", "--disable-gpu", "--window-size=1920,1080", "--virtual-time-budget=2500", "--dump-dom", f"file://{t.resolve()}"], capture_output=True, text=True)
    t.unlink()
    m = re.search(r'<pre id="lintout">(.*?)</pre>', r.stdout, re.S)
    if not m:
        print(f"{sid}: lint did not run"); continue
    import html as H
    res = json.loads(H.unescape(m.group(1)))
    seen = set(); bad = []
    for k, a, b in res:
        if k == "COUNT":
            n = int(a.split()[0])
            if n > 200: bad.append((k, a, "over the 200 element limit"))
            continue
        if (k, b) in seen: continue
        seen.add((k, b)); bad.append((k, a, b))
    total += len(bad)
    print(f"{sid}: {'clean' if not bad else str(len(bad)) + ' defects'}")
    for k, a, b in bad:
        print(f"   {k:5} {a:34} {b}")
print("LINT", "PASS" if total == 0 else f"FAIL ({total})")
sys.exit(0 if total == 0 else 1)
