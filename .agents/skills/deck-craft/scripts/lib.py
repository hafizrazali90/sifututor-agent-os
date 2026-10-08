#!/usr/bin/env python3
"""Deck component library: colours, icons, logo chips, cards, flows, header and footer.
A deck sets DECK["footer"] and fills LOGO from its own logos.json (key -> /_blob/<asset id>)."""
import json
from pathlib import Path
import re


MONO = "font-family:'Geist Mono', 'Courier New', monospace"
NAVY, MUTED, SUB = "#0B1B2B", "#475467", "#5F6672"
TEAL, TEALT = "#0F766E", "#E6F4F1"
BLUE, BLUET = "#2563EB", "#EAF1FE"
AMB, AMBT = "#B45309", "#FEF3E2"
RED, REDT = "#B42318", "#FDECEC"
BORDER, PANEL, ZONE = "#E3E6EA", "#F5F7FA", "#F3FAF8"

DECK = {"footer": "Title · Draft v0.1 · DD/MM/YYYY · Confidential", "owner": "CLIENT"}
LOGO = {}
_lj = Path.cwd() / "logos.json"
if _lj.exists():
    LOGO.update(json.loads(_lj.read_text()))

ICONS = {
    "server": '<rect width="20" height="8" x="2" y="2" rx="2"/><rect width="20" height="8" x="2" y="14" rx="2"/><path d="M6 6h.01M6 18h.01"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8M16 13H8M16 17H8"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "key": '<path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"/><path d="m21 2-9.6 9.6"/><circle cx="7.5" cy="15.5" r="5.5"/>',
    "sparkle": '<path d="M9.94 14.06 4 16l5.94 1.94L12 24l2.06-6.06L20 16l-5.94-1.94L12 8z" transform="translate(0 -4)"/>',
}


FLOW = '<animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.2s" repeatCount="indefinite"/>'


def icon(name, color, size=24):
    return (f'<svg aria-label="" width="{size}" height="{size}" viewBox="0 0 24 24"><g fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g></svg>')


def tile(name, color, bg, size=52, radius=14, isz=24):
    return (f'<div style="width:{size}px; height:{size}px; flex-shrink:0; background:{bg}; border-radius:{radius}px; display:flex; '
            f'align-items:center; justify-content:center">{icon(name, color, isz)}</div>')


def chip(text, color, bg, mono=True, pad="2px 14px", weight=400):
    fam = MONO + "; " if mono else ""
    return (f'<p style="{fam}font-size:24px; font-weight:{weight}; color:{color}; background:{bg}; border-radius:999px; '
            f'padding:{pad}; white-space:nowrap">{text}</p>')


def logo_chip(key, text, h=28):
    return (f'<div style="display:flex; flex-direction:row; align-items:center; gap:8px; background:#FFFFFF; border:2px solid {BORDER}; '
            f'border-radius:999px; padding:4px 14px 4px 8px"><img src="{LOGO[key]}" alt="{text} logo" style="height:{h}px; width:auto">'
            f'<p style="font-size:24px; font-weight:500; color:{NAVY}; white-space:nowrap">{text}</p></div>')


def round_logo_chip(key, text, size=30):
    """Logo chip for a logo that must be cropped to a circle (wide artwork with a round mark)."""
    return (f'<div style="display:flex; flex-direction:row; align-items:center; gap:8px; background:#FFFFFF; border:2px solid {BORDER}; '
            f'border-radius:999px; padding:4px 14px 4px 8px"><div style="width:{size}px; height:{size}px; flex-shrink:0; overflow:hidden; border-radius:{size//2}px">'
            f'<img src="{LOGO[key]}" alt="{text} logo" style="height:{size}px; width:auto; max-width:none"></div>'
            f'<p style="font-size:24px; font-weight:500; color:{NAVY}; white-space:nowrap">{text}</p></div>')


def head(eyebrow, title, lede=None):
    s = (f'<p style="position:absolute; left:128px; top:128px; width:900px; {MONO}; font-size:24px; font-weight:500; letter-spacing:1px; '
         f'text-transform:uppercase; color:{TEAL}">{eyebrow}</p>\n'
         f'<h2 style="position:absolute; left:128px; top:170px; width:1664px; font-family:\'Geist\', Arial, sans-serif; font-size:56px; '
         f'font-weight:600; line-height:1.08; letter-spacing:-1.5px; color:{NAVY}">{title}</h2>\n')
    if lede:
        s += f'<p style="position:absolute; left:128px; top:252px; width:1560px; font-size:26px; line-height:1.4; color:{MUTED}">{lede}</p>\n'
    return s


def footer(page, text=None):
    text = text or DECK["footer"]
    s = (f'<p style="position:absolute; left:128px; bottom:64px; width:1400px; font-size:24px; color:{SUB}">'
         f'<span style="color:{NAVY}"><b>{DECK["owner"]}</b></span> · {text}</p>\n')
    if page:
        s += (f'<p style="position:absolute; right:128px; bottom:64px; width:120px; {MONO}; font-size:24px; color:{SUB}; '
              f'text-align:right">{page}</p>\n')
    return s


def dots(pid, extra="", color="#DDE2E8"):
    return (f'<svg aria-label="" style="position:absolute; left:0px; top:0px" width="1920" height="1080" viewBox="0 0 1920 1080">'
            f'<defs><pattern id="{pid}" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.5" fill="{color}"/>'
            f'</pattern></defs><rect width="1920" height="1080" fill="url(#{pid})"/>{extra}</svg>\n')


def autobuilds(html):
    def fix(m):
        v = m.group(1)
        return m.group(0) if "auto" in v.split() else f'data-build-in="{v} auto"'
    return re.sub(r'data-build-in="([^"]+)"', fix, html)


def section(sid, body, notes, bg="#FFFFFF", transition="fade"):
    body = autobuilds(body)
    return (f'<section id="{sid}" data-transition="{transition}" style="background:{bg}; color:{NAVY}; font-family:\'Geist\', Arial, sans-serif; '
            f'padding:128px 128px 160px; display:flex; flex-direction:column">\n{body}<aside>{notes}</aside>\n</section>\n')


ICONS.update({
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "flag": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><path d="M4 22v-7"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "eye": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "building": '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10M12 3v18M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>',
    "trash": '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "banknote": '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "power": '<path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.77.04"/>',
    "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 17V9M13 17V5M8 17v-3"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "network": '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3M12 12V8"/>',
})
GREY = "#98A2B3"


def pinned(x, y, w, inner, h=None, extra="", build=None):
    hh = f" height:{h}px;" if h else ""
    b = f' data-build-in="{build}"' if build else ""
    return f'<div{b} style="position:absolute; left:{x}px; top:{y}px; width:{w}px;{hh} {extra}">{inner}</div>\n'


def card(x, y, w, h, inner, border=None, bg="#FFFFFF", radius=20, pad="22px 24px", gap=12, shadow=True, build=None, bw=2, dash=False):
    border = border or BORDER
    sh = " box-shadow:0 12px 32px rgba(11,27,43,0.06);" if shadow else ""
    st = "dashed" if dash else "solid"
    return pinned(x, y, w, inner, h, f"background:{bg}; border:{bw}px {st} {border}; border-radius:{radius}px; padding:{pad}; display:flex; flex-direction:column; gap:{gap}px;{sh}", build)


def P(text, size=24, color=None, weight=400, mono=False, lh=1.35, extra=""):
    fam = MONO + "; " if mono else ""
    return f'<p style="{fam}font-size:{size}px; font-weight:{weight}; line-height:{lh}; color:{color or NAVY}; {extra}">{text}</p>'


def row(inner, gap=12, align="center", extra=""):
    return f'<div style="display:flex; flex-direction:row; align-items:{align}; gap:{gap}px; {extra}">{inner}</div>'


def col(inner, gap=8, extra=""):
    return f'<div style="display:flex; flex-direction:column; gap:{gap}px; {extra}">{inner}</div>'


def label(text, color=None):
    return f'<p style="{MONO}; font-size:24px; font-weight:500; letter-spacing:1px; text-transform:uppercase; color:{color or SUB}">{text}</p>'


def svg(inner):
    return f'<svg aria-label="" style="position:absolute; left:0px; top:0px" width="1920" height="1080" viewBox="0 0 1920 1080">{inner}</svg>\n'


def flowline(x1, y1, x2, y2, color=None, dash=True, arrow=True, w=2.5, animate=True):
    color = color or TEAL
    d = ' stroke-dasharray="8 6"' if dash else ""
    an = FLOW if (dash and animate) else ""
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d}>{an}</line>'
    if arrow:
        import math
        a = math.atan2(y2 - y1, x2 - x1); k = 13
        pts = [(x2, y2), (x2 - k * math.cos(a - 0.45), y2 - k * math.sin(a - 0.45)), (x2 - k * math.cos(a + 0.45), y2 - k * math.sin(a + 0.45))]
        s += '<polygon points="' + " ".join(f"{px:.1f},{py:.1f}" for px, py in pts) + f'" fill="{color}"/>'
    return s


def yes(color=None):
    return icon("check", color or TEAL)


def no():
    return icon("x", GREY)


def doc(name, color=None):
    """A small file row: coloured file icon and a mono file name."""
    return (f'<div style="background:#FFFFFF; border:2px solid {BORDER}; border-radius:10px; padding:8px 12px; display:flex; flex-direction:row; align-items:center; gap:10px">'
            f'{icon("file", color or BLUE)}<p style="{MONO}; font-size:24px; color:{NAVY}">{name}</p></div>')


def skel(w="100%"):
    return f'<div style="width:{w}; height:10px; background:#E6E9EE; border-radius:5px"></div>'


def numdot(n, color, size=52, fs=28):
    return (f'<div style="width:{size}px; height:{size}px; border-radius:{size//2}px; background:{color}; display:flex; align-items:center; justify-content:center; flex-shrink:0">'
            f'<p style="font-size:{fs}px; font-weight:600; color:#FFFFFF">{n}</p></div>')


def strip(x, y, w, h, inner, bg, build=None, extra=""):
    return pinned(x, y, w, inner, h, f"background:{bg}; border-radius:18px; padding:0 22px; display:flex; align-items:center; {extra}", build)


PG = {}


def pg(sid):
    return PG.get(sid, "")
