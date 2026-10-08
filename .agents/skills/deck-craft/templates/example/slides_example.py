"""Two example slides: a flow with icon tiles and badges, and a dark close."""
from lib import *  # noqa: F401,F403


def flow():
    b = dots("dots-flow")
    b += head("Example · flow", "One request, four steps, each with an owner.",
              "Every slide carries one real graphic. This one is a left-to-right flow with icon tiles, badges and a note strip.")
    steps = [("users", "Ask", "staff, English or Malay", TEAL, TEALT, ["Draft the reply to this tender.", None]),
             ("lock", "Check", "Microsoft sign-in", BLUE, BLUET, ["group: ILSAS trainers", "library: tenders"]),
             ("search", "Find", "approved files only", AMB, AMBT, [doc("tender_2025.docx", RED), "p. 12, p. 14"]),
             ("check", "Answer", "with source and page", TEAL, TEALT, [doc("reply_draft.docx", TEAL), "a person checks"])]
    ln = ""
    for i, (ic, t, d, c, bg, mock) in enumerate(steps):
        x = 128 + i * 424
        inner = "".join(m if m and m.startswith("<") else (P(m, 24, NAVY) if m else skel("70%")) for m in mock)
        panel = f'<div style="flex:1; background:{PANEL}; border-radius:14px; padding:14px; display:flex; flex-direction:column; gap:10px">{inner}{skel()}{skel("60%")}</div>'
        b += card(x, 360, 392, 380, row(tile(ic, c, bg) + P(t, 32, NAVY, 600) + '<div style="flex:1"></div>' + chip(f"step {i+1}", c, bg), gap=14) + P(d, 26, MUTED) + panel,
                  pad="24px 26px", gap=14, build=f"rise {i+1}")
        if i < 3:
            ln += flowline(x + 392, 550, x + 424, 550, TEAL, dash=True)
    b += svg(ln)
    b += strip(128, 790, 1664, 140, row(tile("alert", "#FFFFFF", AMB, 48, 12) + col(P("Limits, stated plainly", 28, NAVY, 600) +
               P("The assistant can be wrong. A person checks every answer.", 24, MUTED), gap=2, extra="flex:1"), gap=18, extra="flex:1"), AMBT, "rise 5")
    b += footer(pg("flow"))
    return section("flow", b, "In one sentence: an example. If asked: none.")


def close():
    b = f'<h1 style="position:absolute; left:128px; top:420px; width:1200px; font-size:80px; font-weight:600; color:#FFFFFF">Example close slide.</h1>\n'
    b += footer(pg("close"))
    return section("close", b, "In one sentence: close. If asked: none.", bg=NAVY)


SLIDES = [flow, close]
