"""Builds kota-buku-deck.template.html (14 slides) from the three-slide sample template.
Hafiz, 07/09/2026: cool grey ground and light chrome, cover in the big-headline style, 14 merged slides,
every non-sample slide on the sample's hierarchy (one workspace panel, a three-step strip, numbered callouts,
one dominant region, nothing empty at rest)."""
import base64, json, re, sys
sys.path.insert(0, '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/build')
from deck2_content import EN, BM
D = '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/'
s = open(D + 'kota-buku-sequence.template.html').read()

def b64(name):
    return "data:image/jpeg;base64," + base64.b64encode(open(D + 'assets/' + name, 'rb').read()).decode()
EN['b07i2'] = EN['b07i'] + ' ' + EN['b08i']; BM['b07i2'] = BM['b07i'] + ' ' + BM['b08i']
IMG = {k: b64(v) for k, v in {'teacher': 'teacher-slide1.jpg', 'pupils': 'deck-pupils-paper-web.jpg', 'parent': 'deck-parent-phone-web.jpg', 'older': 'deck-older-pupil-web.jpg'}.items()}

def rep(a, b, count=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, count)

# =====================================================================
# CSS
# =====================================================================
CSS = r'''
/* ===========================================
   DECK: shared parts
   =========================================== */
:root{--stage-bg:#e9e9ec;--slide-bg:#f5f5f7;--line:#E2E3E8;--line-soft:#ECEDF1;--soft:#F9F9FB}
.stagebox{position:absolute;left:120px;top:300px;width:1680px;height:600px}
.info{display:inline-flex;vertical-align:middle;margin-left:12px;width:30px;height:30px;border-radius:50%;border:1.5px solid var(--line);background:var(--surface);color:var(--accent-ink);font-family:var(--display);font-weight:700;font-size:15px;cursor:pointer;align-items:center;justify-content:center;position:relative;top:-2px}
.subwrap{display:inline-block;max-width:1400px;margin-top:12px}
.subwrap .sub{display:inline;margin:0}
.infocard{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:1040px;max-height:820px;background:var(--surface);border:1px solid var(--line);border-radius:22px;box-shadow:0 30px 80px rgba(26,31,36,.18);padding:36px 40px;z-index:12;display:none;flex-direction:column;gap:14px}
.infocard.show{display:flex}
.infocard h3{font-family:var(--display);font-weight:600;font-size:24px;line-height:1.2}
.infocard p{font-size:20px;line-height:1.55;color:var(--ink)}
.infocard .close{order:-1;align-self:flex-end;font-size:16px;font-weight:600;padding:9px 16px;border-radius:10px;border:1px solid var(--line);background:var(--surface);cursor:pointer;font-family:var(--body)}
.scrim{position:absolute;inset:0;background:rgba(26,31,36,.28);z-index:11;display:none}
.scrim.show{display:block}
.pcard{position:absolute;border-radius:22px;overflow:hidden;background:var(--line-soft);border:1px solid var(--line);box-shadow:var(--shadow)}
.im{position:absolute;inset:0;background-size:cover;background-position:center;border-radius:inherit}
.pcard .cap{position:absolute;left:0;right:0;bottom:0;padding:16px 20px;background:linear-gradient(180deg,rgba(26,31,36,0) 0%,rgba(26,31,36,.78) 100%);color:#fff}
.pcard .cap b{display:block;font-family:var(--display);font-weight:600;font-size:22px}
.pcard .cap span{font-size:16px;opacity:.92}
.pcard .note{position:absolute;left:16px;top:16px}
.pcard.on{box-shadow:0 0 0 3px var(--accent),var(--shadow)}
.mark{display:inline-flex;align-items:center;gap:8px;font-size:15px;font-weight:600;color:var(--accent-ink);background:var(--accent-soft);border-radius:999px;padding:6px 12px}
.pillnote{display:inline-flex;align-items:center;gap:8px;font-size:16px;font-weight:600;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:8px 14px}
.pillnote.trial{color:var(--trial);border-color:var(--trial);background:var(--trial-soft)}
.pillnote.good{color:var(--good);border-color:#BFE0CC;background:var(--good-soft)}
.chipline{display:inline-flex;align-items:center;gap:10px;font-size:16px;color:var(--muted)}
.hintt{font-size:15px;color:var(--muted)}
.prov.tpl{background:var(--accent-soft);color:var(--accent-ink);border:1px solid var(--accent-soft)}
.btn.done{opacity:.55;pointer-events:none}
.empty{color:var(--muted);font-style:italic}
/* workspace panel: the sample's slide 2 grammar for every proposed screen */
.p2{position:absolute;left:120px;top:300px;width:1680px;height:600px;background:var(--surface);border:1px solid var(--line);border-radius:22px;box-shadow:var(--shadow)}
.strip2{position:absolute;left:0;right:0;top:0;height:54px;display:flex;align-items:center;gap:30px;padding:0 26px;border-bottom:1px solid var(--line-soft);font-size:17px;font-weight:600;color:var(--ink)}
.strip2 .st2{display:inline-flex;align-items:center;gap:10px}
.strip2 .st2 i{width:26px;height:26px;border-radius:50%;background:var(--ink);color:#fff;font-style:normal;font-family:var(--display);font-weight:700;font-size:14px;display:inline-flex;align-items:center;justify-content:center}
.strip2 .st2.hi i{background:var(--hi);color:var(--hi-ink)}
.strip2 .key{margin-left:auto;display:inline-flex;gap:14px;font-size:15px;font-weight:500;color:var(--muted)}
.strip2 .key span{display:inline-flex;align-items:center;gap:6px}
.strip2 .key i{width:18px;height:12px;border-radius:3px;display:inline-block}
.strip2 .key i.ai{background:var(--hi)}.strip2 .key i.me{background:#fff;border:1px solid var(--line)}.strip2 .key i.tp{background:var(--accent-soft)}
.bd{position:absolute;left:0;right:0;top:55px;bottom:0;padding:22px 26px;display:grid;gap:26px}
.co{position:absolute;width:40px;height:40px;border-radius:50%;background:var(--ink);color:#fff;font-family:var(--display);font-weight:700;font-size:18px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 4px var(--surface);z-index:3}
.co.hi{background:var(--hi);color:var(--hi-ink)}
.h4{font-family:var(--display);font-weight:600;font-size:22px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.h4 .sub2{font-family:var(--body);font-weight:400;font-size:15px;color:var(--muted)}
.h4 .n{width:30px;height:30px;border-radius:50%;background:var(--ink);color:#fff;font-family:var(--display);font-weight:700;font-size:15px;display:inline-flex;align-items:center;justify-content:center;flex:none;margin-right:10px}
.h4 .n.hi{background:var(--hi);color:var(--hi-ink)}
.h4 .tl{display:inline-flex;align-items:center;margin-right:auto}
/* title slide */
#t0 .tt{position:absolute;left:96px;top:190px;width:900px}
#t0 .tt .k{font-family:var(--display);font-weight:600;font-size:18px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-ink)}
#t0 .tt h1{font-size:96px;line-height:.98;letter-spacing:-.02em;margin:22px 0 28px;text-wrap:balance}
#t0 .tt p{font-size:28px;line-height:1.4;color:var(--muted);max-width:780px}
#t0 .steps{display:flex;align-items:center;gap:18px;margin-top:56px;flex-wrap:wrap}
#t0 .steps .stp{display:flex;flex-direction:column;gap:2px;font-size:19px;color:var(--ink)}
#t0 .steps .stp b{font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
#t0 .steps i{width:26px;height:2px;background:var(--muted);position:relative;flex:none;opacity:.7}
#t0 .steps i::after{content:"";position:absolute;right:-1px;top:-4px;width:8px;height:8px;border-top:2px solid var(--muted);border-right:2px solid var(--muted);transform:rotate(45deg)}
#t0 .card{position:absolute;left:1080px;top:180px;width:760px;height:600px;background:var(--surface);border-radius:28px;box-shadow:0 34px 90px rgba(26,31,36,.12),0 2px 8px rgba(26,31,36,.05);transform:rotate(-3.5deg);padding:52px 60px;display:flex;flex-direction:column;gap:18px}
#t0 .card .lbl{font-family:var(--display);font-weight:600;font-size:15px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
#t0 .card h2{font-family:var(--display);font-weight:700;font-size:44px;line-height:1.1;letter-spacing:-.01em}
#t0 .card .pies{display:flex;align-items:center;gap:26px;margin:14px 0 8px}
#t0 .card .pies .frac{font-size:34px;color:var(--muted)}
#t0 .card .pies .frac span:first-child{border-bottom-color:var(--muted)}
#t0 .card .pies svg:last-child{margin-left:auto}
#t0 .card .q{font-size:28px;line-height:1.35;color:var(--ink)}
#t0 .card .status{align-self:flex-start;margin-top:4px}
/* beat 01: who it serves (three-card section) */
#b01 .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;height:600px}
#b01 .card1{display:flex;flex-direction:column;gap:14px;cursor:pointer}
#b01 .ph{position:relative;height:420px;border-radius:24px;overflow:hidden;border:1px solid var(--line);box-shadow:var(--shadow);background:var(--line-soft)}
#b01 .tag2{position:absolute;left:18px;top:18px;background:var(--surface);border-radius:999px;padding:8px 14px;font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink);box-shadow:0 2px 6px rgba(26,31,36,.08)}
#b01 .card1 > b{font-family:var(--display);font-weight:600;font-size:26px;margin-top:8px;align-self:flex-start}
#b01 .card1 > span{font-size:19px;line-height:1.45;color:var(--muted)}
#b01 .card1.on .ph{box-shadow:0 0 0 3px var(--accent),var(--shadow)}
#b01 .card1.on > span{color:var(--ink)}
/* beat 02: one topic through the lesson (step section) */
#b02 .tabs{display:flex;gap:10px;margin-bottom:34px}
#b02 .tab{display:inline-flex;align-items:center;gap:10px;padding:10px 18px 10px 12px;border-radius:999px;border:1px solid var(--line);background:var(--surface);font-family:var(--display);font-weight:600;font-size:17px;cursor:pointer;color:var(--muted)}
#b02 .tab i{font-style:normal;font-size:13px;letter-spacing:.06em;color:var(--ink);background:var(--line-soft);border-radius:999px;padding:3px 8px}
#b02 .tab.on{border-color:var(--accent);background:var(--accent-soft);color:var(--accent-ink)}
#b02 .tab.on i{background:var(--accent);color:#fff}
#b02 .two{display:grid;grid-template-columns:720px 1fr;gap:60px;align-items:start}
#b02 .txt{display:flex;flex-direction:column;gap:18px}
#b02 .eb{font-family:var(--display);font-weight:600;font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-ink);display:inline-flex;align-items:center;gap:8px}
#b02 .eb .dot{width:5px;height:5px;border-radius:50%;background:var(--accent-ink);display:inline-block}
#b02 h2{font-family:var(--display);font-weight:700;font-size:44px;line-height:1.1;letter-spacing:-.01em}
#b02 .txt p{font-size:21px;line-height:1.45;color:var(--muted)}
#b02 ul{list-style:none;display:flex;flex-direction:column;gap:12px;margin-top:6px}
#b02 li{display:flex;gap:12px;align-items:center;font-size:19px}
#b02 li i{width:22px;height:22px;border-radius:50%;background:var(--accent);flex:none;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat}
#b02 .txt .mark{align-self:flex-start;margin-top:8px}
#b02 .vis{position:relative;height:500px;border-radius:24px;background:var(--accent-soft);overflow:hidden}
#b02 .v{position:absolute;inset:0;display:none;align-items:center;justify-content:center;padding:36px}
#b02 .v.on{display:flex}
#b02 .mock{width:100%;max-width:760px;background:var(--surface);border:1px solid var(--line);border-radius:20px;box-shadow:0 24px 60px rgba(26,31,36,.10);padding:32px 36px;display:flex;flex-direction:column;gap:16px}
#b02 .mock .mt{font-family:var(--display);font-weight:600;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
#b02 .mock .mv{font-family:var(--display);font-weight:700;font-size:30px}
#b02 .mock .mv.big{font-size:34px;line-height:1.3}
#b02 .mock .row{display:grid;grid-template-columns:170px 1fr;gap:14px;font-size:18px;line-height:1.4;padding:14px 16px;border-radius:10px;background:var(--soft);border:1px solid var(--line-soft)}
#b02 .mock .row b{font-weight:600;color:var(--muted);font-size:16px}
#b02 .mock .row.hl{background:var(--accent-soft);border-color:transparent}
#b02 .mock .pr{display:flex;align-items:center;gap:12px;font-size:18px}
#b02 .mock .prov{font-size:16px;padding:6px 12px}
#b02 .mock .mark{font-size:16px;align-self:flex-start}
#b02 .mock svg{display:block;margin-top:8px;width:100%;height:auto}
#b02 .bub2{display:grid;grid-template-columns:36px repeat(4,1fr);gap:10px;align-items:center;font-size:17px;color:var(--muted);max-width:520px}
#b02 .bub2 em{font-style:normal;text-align:center;font-weight:600}
#b02 .bub2 i{width:28px;height:28px;border-radius:50%;border:2px solid var(--ink);display:inline-block;justify-self:center}
#b02 .bub2 i.f{background:var(--ink);box-shadow:0 0 0 3px var(--accent-soft)}
#b02 .bars2{display:flex;gap:18px;align-items:stretch;height:200px;margin-top:28px}
#b02 .bars2 div{flex:1;background:var(--accent-soft);border-radius:8px 8px 4px 4px;position:relative;display:flex;align-items:flex-end}
#b02 .bars2 div i{position:absolute;top:-26px;left:0;right:0;text-align:center;font-style:normal;font-size:17px;font-weight:600;color:var(--accent-ink)}
#b02 .bars2 div s{display:block;width:100%;background:var(--accent);border-radius:8px 8px 4px 4px;text-decoration:none}
/* beat 05: pupils on paper (scan pattern) */
#b05 .bd{grid-template-columns:1fr 600px}
#b05 .cam{position:relative;border-radius:18px;background:#1B2328;overflow:hidden;display:flex;align-items:center;justify-content:center}
#b05 .hint{position:absolute;left:50%;top:22px;transform:translateX(-50%);color:#fff;font-size:16px;font-weight:600;background:rgba(0,0,0,.45);border-radius:999px;padding:8px 16px;white-space:nowrap}
#b05 .sheet2{width:540px;background:#fff;border-radius:6px;padding:18px 24px;transform:rotate(-2deg);box-shadow:0 14px 40px rgba(0,0,0,.35),0 0 0 3px var(--accent);display:flex;flex-direction:column;gap:4px}
#b05 .sheet2 .t{font-family:var(--display);font-weight:600;font-size:17px;color:var(--ink)}
#b05 .sheet2 .n{font-size:13px;color:var(--muted);margin-bottom:6px;display:flex;justify-content:space-between}
#b05 .sheet2 .n s{text-decoration:none;display:inline-block;min-width:150px;font-family:'Comic Sans MS','Bradley Hand',cursive;font-size:14px;color:#1f3b8a;border-bottom:1.5px solid var(--line);padding:0 6px 1px;line-height:1.1}
#b05 .bub{display:grid;grid-template-columns:32px repeat(4,1fr);gap:1px 6px;align-items:center;font-size:13px;color:var(--muted);margin-top:4px}
#b05 .bub em{font-style:normal;text-align:center;font-weight:600}
#b05 .bub i{width:19px;height:19px;border-radius:50%;border:2px solid var(--ink);display:inline-block;justify-self:center}
#b05 .bub i.f{background:var(--ink)}
#b05 .thumb{position:absolute;right:26px;bottom:24px;width:54px;height:70px;background:#fff;border-radius:4px;box-shadow:0 4px 14px rgba(0,0,0,.4);padding:8px 7px;display:none;flex-direction:column;gap:5px}
#b05 .thumb b{height:6px;width:70%;background:var(--ink);border-radius:2px;opacity:.7}
#b05 .thumb s{height:4px;width:100%;background:var(--line);border-radius:2px;text-decoration:none}
#b05 .cam.read .thumb{display:flex}
#b05 .shutter2{position:absolute;left:50%;bottom:20px;transform:translateX(-50%);width:66px;height:66px;border-radius:50%;background:#fff;box-shadow:0 0 0 3px #1B2328,0 0 0 6px #fff;cursor:pointer}
#b05 .shutter2.busy{opacity:.5;pointer-events:none}
#b05 .res2{display:flex;flex-direction:column;gap:14px;border-left:1px solid var(--line-soft);padding-left:26px}
#b05 .bigread{font-family:var(--display);font-weight:700;font-size:34px;letter-spacing:-.01em}
#b05 .alabel{font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:4px}
#b05 .chips{display:grid;grid-template-columns:repeat(10,1fr);gap:6px}
#b05 .ch{display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 0 6px;border-radius:9px;background:var(--good-soft);color:var(--good);font-family:var(--display);font-weight:700;font-size:18px}
#b05 .ch small{font-size:13px;font-weight:600;color:var(--muted);font-family:var(--body)}
#b05 .ch.u{background:#FBEFD6;color:#7A4B00;box-shadow:inset 0 0 0 2px #E4A33B}
#b05 .ch.ok{background:var(--good-soft);color:var(--good);box-shadow:none}
#b05 .rows{display:flex;flex-direction:column;gap:8px;margin-top:4px}
#b05 .rows .row{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:17px;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:#fff}
#b05 .rows .row b{font-weight:600}
#b05 .btn.small{font-size:15px;padding:7px 12px}
#b05 .res2 .acts{margin-top:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
/* beat 06: class view and the assistant (dashboard pattern) */
#b06 .bd{grid-template-columns:1fr 560px}
#b06 .cls{display:flex;flex-direction:column;gap:14px;min-height:0}
#b06 .sum{display:grid;grid-template-columns:200px 1fr;gap:28px;align-items:start;padding:10px 18px;border-radius:14px;background:var(--soft);border:1px solid var(--line-soft)}
#b06 .stats{display:flex;flex-direction:column;gap:2px}
#b06 .stat{display:flex;align-items:baseline;gap:10px}
#b06 .stat b{font-family:var(--display);font-weight:700;font-size:24px;letter-spacing:-.01em;min-width:64px}
#b06 .stat b small{font-size:15px;color:var(--muted);font-weight:600}
#b06 .stat span{font-size:14.5px;color:var(--muted)}
#b06 .tbars{display:flex;flex-direction:column;gap:5px}
#b06 .tb{display:grid;grid-template-columns:190px 1fr 96px;gap:12px;align-items:center;font-size:14.5px}
#b06 .seg{display:flex;height:14px;border-radius:5px;overflow:hidden;gap:2px}
#b06 .seg i{display:block;height:100%}
#b06 .seg i.s,#b06 .dot.s{background:#8FCDAB}#b06 .seg i.a,#b06 .dot.a{background:#F0C97A}#b06 .seg i.n,#b06 .dot.n{background:#E39A9A}
#b06 .cnt{font-size:13.5px;color:var(--muted);text-align:right;white-space:nowrap}
#b06 .cnt em{font-style:normal;opacity:.5}
#b06 .lg{display:flex;gap:16px;font-size:15px;color:var(--muted);margin-top:2px}
#b06 .lg span{display:inline-flex;align-items:center;gap:6px}
#b06 .dot{width:14px;height:14px;border-radius:50%;display:inline-block}
#b06 .tbl{display:flex;flex-direction:column;gap:2px}
#b06 .tr{display:grid;grid-template-columns:150px 1fr 112px 88px;gap:12px;align-items:center;padding:3px 10px;border-radius:9px;font-size:15px;cursor:pointer}
#b06 .tr.hd{font-family:var(--display);font-weight:600;font-size:13.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);cursor:default;padding-bottom:4px;border-bottom:1px solid var(--line-soft);border-radius:0}
#b06 .tr:not(.hd):not(.det):not(.more):hover{background:var(--soft)}
#b06 .tr.on{background:var(--accent-soft)}
#b06 .tr.more{cursor:default;color:var(--muted);font-style:italic;padding-top:2px}
#b06 .tr b{font-weight:600;text-align:right}
#b06 .hl{display:inline-flex;align-items:center;font-size:14px;font-weight:600;padding:3px 10px;border-radius:999px;white-space:nowrap;max-width:100%;overflow:hidden}
#b06 .hl span{overflow:hidden;text-overflow:ellipsis}
#b06 .hl.hlN{background:#F8E7E7;color:#8C2F39}#b06 .hl.hlOk{background:var(--good-soft);color:var(--good)}#b06 .hl.hlA{background:#FBEFD6;color:#7A4B00}
#b06 .dots{display:flex;gap:7px}
#b06 .tr.det{display:none;grid-column:1/-1;grid-template-columns:auto 1fr auto;gap:16px;background:var(--soft);border:1px solid var(--line-soft);padding:7px 14px;cursor:default;font-size:14.5px;position:relative}
#b06 .tr.det.show{display:grid}
#b06 .tr.det b{font-family:var(--display);font-weight:600;font-size:16px;text-align:left}
#b06 .tr.det .items{display:flex;gap:4px}
#b06 .tr.det .items span{width:28px;height:24px;border-radius:6px;background:var(--good-soft);color:var(--good);font-weight:600;font-size:13px;display:inline-flex;align-items:center;justify-content:center}
#b06 .tr.det .items span.x{background:#F8E7E7;color:#8C2F39}
#b06 .tr.det .why{color:var(--muted);white-space:nowrap}
#b06 .ins{display:flex;flex-direction:column;gap:12px;border-left:1px solid var(--line-soft);padding-left:26px;min-height:0}
#b06 .ins > *{flex-shrink:0}
#b06 .flag{display:flex;align-items:center;gap:12px;font-size:15px;line-height:1.35;background:var(--soft);border:1px solid var(--line-soft);border-radius:12px;padding:10px 14px}
#b06 .askT{display:flex;align-items:baseline;justify-content:space-between;gap:10px;font-family:var(--display);font-weight:600;font-size:17px;margin-top:2px}
#b06 .qs{display:flex;flex-wrap:wrap;gap:8px}
#b06 .qs .btn{font-size:14.5px;padding:6px 11px;border-radius:999px}
#b06 .qs .btn.on{background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink)}
#b06 .ans{background:var(--ai-tint);border:1px solid var(--hi-line);border-radius:12px;padding:10px 12px;font-size:15.5px;line-height:1.42;min-height:100px;display:flex;flex-direction:column;gap:8px}
#b06 .ans .prov{align-self:flex-start}
#b06 .acts{display:grid;grid-template-columns:1fr 1fr;gap:8px}
#b06 .acts .btn{justify-content:center}
#b06 .acts .btn{font-size:14.5px;padding:7px 11px}
/* admin assistant */
#b06c .bd{grid-template-columns:520px 1fr}
#b06c .tasks{display:flex;flex-direction:column;gap:10px}
#b06c .task{display:flex;flex-direction:column;gap:4px;padding:14px 16px;border-radius:14px;border:1px solid var(--line);cursor:pointer;background:#fff}
#b06c .task.on{background:var(--accent-soft);border-color:var(--accent)}
#b06c .task b{font-family:var(--display);font-weight:600;font-size:19px;display:flex;justify-content:space-between;align-items:center;gap:10px}
#b06c .task .src{font-size:14.5px;color:var(--muted);line-height:1.3}
#b06c .task .stp{font-size:13.5px;font-weight:600;padding:4px 9px;border-radius:6px;background:var(--line-soft);color:var(--muted);white-space:nowrap}
#b06c .task .stp.ok{background:var(--good-soft);color:var(--good)}
#b06c .draft{display:flex;flex-direction:column;gap:12px;border-left:1px solid var(--line-soft);padding-left:26px}
#b06c .draft .to{display:flex;align-items:center;gap:12px;font-size:16px;color:var(--muted)}
#b06c .draft .to .prov{margin-left:auto}
#b06c .dtext{flex:0 0 auto;min-height:150px;border-radius:14px;padding:22px 24px;font-size:21px;line-height:1.5;color:var(--ink)}
#b06c .sentbox{margin-top:auto;background:var(--soft);border:1px solid var(--line-soft);border-radius:12px;padding:12px 16px;display:flex;flex-direction:column;gap:6px;font-size:15px}
#b06c .sentbox b{font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
#b06c .sentbox span{display:flex;justify-content:space-between;gap:12px}
#b06c .sentbox span em{font-style:normal;color:var(--muted)}
#b06c .dtext.tpl{background:var(--soft);border:1px solid var(--line-soft)}
#b06c .dtext.ai{background:var(--ai-tint);border:1px solid var(--hi-line)}
#b06c .dacts{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
/* data: inputs and outputs (Runner pattern) */
#b06d .bd{grid-template-columns:1fr 1fr;gap:26px}
#b06d .dcol{display:flex;flex-direction:column;gap:16px;min-height:0}
#b06d .dcol > *{flex-shrink:0}
#b06d .dcard{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 20px;display:flex;flex-direction:column;gap:10px}
#b06d .dcard.oc{background:var(--soft);border-color:var(--line-soft)}
#b06d .dcard.out{background:var(--ai-tint);border-color:var(--hi-line)}
#b06d .lbl{display:inline-flex;align-items:center;gap:8px;font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
#b06d .lbl .n{width:24px;height:24px;font-size:13px;margin-right:2px;border-radius:50%;background:var(--ink);color:#fff;font-style:normal;display:inline-flex;align-items:center;justify-content:center;letter-spacing:0}
#b06d .lbl .n.hi{background:var(--hi);color:var(--hi-ink)}
#b06d .chips2{display:flex;flex-wrap:wrap;gap:8px}
#b06d .chips2 span{font-size:15.5px;font-weight:600;padding:7px 12px;border-radius:999px;background:var(--soft);border:1px solid var(--line)}
#b06d .dcard p{font-size:16px;line-height:1.45;color:var(--ink)}
#b06d .dcard .quote{font-size:19px;line-height:1.4;font-style:italic}
#b06d .dcard.q .btn{align-self:flex-start;font-size:16px;padding:9px 16px}
#b06d .dout{font-size:18px;line-height:1.45;display:flex;flex-direction:column;gap:8px;min-height:74px}
#b06d .dout .prov{align-self:flex-start}
#b06d .dcard ul{list-style:none;display:flex;flex-direction:column;gap:8px}
#b06d .dcard li{display:flex;gap:10px;align-items:flex-start;font-size:16px;line-height:1.35}
#b06d .dcard li i{width:20px;height:20px;border-radius:50%;background:var(--good);flex:none;margin-top:2px;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat}
/* families (two-card pattern, whole phone visible) */
#b07 .fcards{display:grid;grid-template-columns:1fr 1fr;gap:40px;height:548px}
#b07 .fcard{background:var(--surface);border:1px solid var(--line);border-radius:22px;box-shadow:var(--shadow);padding:26px 30px;display:grid;grid-template-columns:268px 1fr;gap:30px;align-items:center}
#b07 .devwrap{position:relative;width:268px;height:496px}
#b07 .dev{position:absolute;left:0;top:0;width:335px;height:620px;border-radius:44px;background:#1B2328;padding:10px;box-shadow:0 18px 40px rgba(26,31,36,.18);transform:scale(.8);transform-origin:0 0}
#b07 .dev .phone{width:100%;height:100%;border-radius:36px;border:0;box-shadow:none}
#b07 .dev .pbar{position:relative}
#b07 .dev .notch{position:absolute;left:50%;top:8px;transform:translateX(-50%);width:96px;height:22px;border-radius:999px;background:#1B2328}
#b07 .ftext{display:flex;flex-direction:column;gap:12px}
#b07 .fcard > .ftext > b{font-family:var(--display);font-weight:700;font-size:28px;line-height:1.15}
#b07 .fcard > .ftext > p{font-size:18px;line-height:1.45;color:var(--muted)}
#b07 .fcard ul{list-style:none;display:flex;flex-direction:column;gap:8px;margin-top:6px}
#b07 .fcard li{display:flex;gap:12px;align-items:center;font-size:17.5px}
#b07 .fcard li i{width:22px;height:22px;border-radius:50%;background:var(--good);flex:none;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat}
#b07 .fnote{position:absolute;left:0;right:0;bottom:0;text-align:center;font-size:17px;color:var(--muted)}
.phone{width:360px;height:560px;border-radius:34px;background:var(--surface);border:1.5px solid var(--line);box-shadow:var(--shadow);overflow:hidden;display:flex;flex-direction:column;position:relative}
.phone .pbar{height:44px;display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--muted);border-bottom:1px solid var(--line-soft)}
.phone .pbody{padding:14px 16px;display:flex;flex-direction:column;gap:10px;font-size:15px;overflow:hidden}
.phone h4{font-family:var(--display);font-weight:600;font-size:19px}
.phone .who{font-size:13.5px;color:var(--muted);margin-top:-6px}
.phone .sec{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.phone .sec b{display:block;font-size:13.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;font-weight:600}
.phone .sec p{font-size:15.5px;line-height:1.35}
.phone .sec.hl{background:var(--accent-soft);border-color:transparent}
.phone .foot{margin-top:auto;font-size:14.5px;color:var(--muted);text-align:center;padding:10px}
/* content */
#b09 .grid{display:grid;grid-template-columns:1fr 60px 1fr;gap:20px;align-items:stretch;margin-top:50px}
#b09 .page{position:relative;background:#FFFDF9;border:1px solid var(--line);border-radius:14px;padding:30px 34px;display:flex;flex-direction:column;gap:12px;box-shadow:var(--shadow)}
#b09 .page .ch{font-family:var(--display);font-weight:600;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
#b09 .page h4{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:28px}
#b09 .page p{font-family:"Source Serif 4",Georgia,serif;font-size:19px;line-height:1.6}
#b09 .page .fig{display:flex;flex-direction:column;gap:8px;margin-top:6px}
#b09 .page .fig svg{display:block;max-width:100%}
#b09 .page .fig span{font-family:"Source Serif 4",Georgia,serif;font-size:16px;color:var(--muted);font-style:italic}
#b09 .page .acts{margin-top:auto;display:flex;flex-direction:column;gap:10px;align-items:flex-start}
#b09 .arrow2{display:flex;align-items:center;justify-content:center;color:var(--accent)}
#b09 .out{position:relative;background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:24px 26px;display:flex;flex-direction:column;gap:14px}
#b09 .out h4{font-family:var(--display);font-weight:600;font-size:22px}
#b09 #pgOut{display:flex;flex-direction:column;gap:14px;align-items:stretch}
#b09 #pgOut .prov{align-self:flex-start}
#b09 .out .d{background:var(--ai-tint);border:1px solid var(--hi-line);border-radius:12px;padding:14px 16px;font-size:18px;line-height:1.45}
#b09 .out .d b{display:block;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--hi-ink);margin-bottom:4px}
#b09 .perm{position:absolute;left:0;top:-8px}
#b09 .co{left:-20px;top:24px}
/* practical and protected */
#b10 .bd{grid-template-columns:580px 420px 1fr}
#b10 .col{display:flex;flex-direction:column;gap:12px}
#b10 .col + .col{border-left:1px solid var(--line-soft);padding-left:26px}
.switch{display:flex;align-items:center;justify-content:space-between;background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:12px 16px;font-size:18px;cursor:pointer}
.switch .tog{width:56px;height:30px;border-radius:999px;background:var(--good);position:relative;transition:background .2s}
.switch .tog::after{content:"";position:absolute;top:3px;left:29px;width:24px;height:24px;border-radius:50%;background:#fff;transition:left .2s}
.switch.off .tog{background:var(--line)}
.switch.off .tog::after{left:3px}
#b10 .wl{display:flex;flex-direction:column;gap:8px}
#b10 .wl .row{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:17px;padding:11px 14px;border:1px solid var(--line);border-radius:12px}
#b10 .wl .row .st{font-size:14.5px;font-weight:600;padding:4px 9px;border-radius:6px;background:var(--good-soft);color:var(--good)}
#b10 .wl .row.need .st{background:var(--line-soft);color:var(--muted)}
#b10 .wl .row.need.off{opacity:.5}
#b10 ol{padding-left:22px;display:flex;flex-direction:column;gap:10px;font-size:17.5px;line-height:1.35}
#b10 .langs{display:flex;flex-wrap:wrap;gap:8px}
#b10 .langs span{font-size:16px;font-weight:600;padding:8px 13px;border-radius:999px;border:1.5px solid var(--accent);color:var(--accent-ink);background:var(--accent-soft)}
#b10 .col p{font-size:16.5px;color:var(--muted);line-height:1.4}
#b10 .seg{display:flex;gap:6px;background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:5px}
#b10 .seg .role{flex:1;text-align:center;padding:10px 6px;border-radius:9px;font-family:var(--display);font-weight:600;font-size:16px;cursor:pointer}
#b10 .seg .role.on{background:var(--surface);box-shadow:0 1px 4px rgba(26,31,36,.12)}
#b10 .sees{font-size:20px;line-height:1.35;background:var(--accent-soft);border-radius:12px;padding:16px 18px;color:var(--accent-ink);font-weight:600;min-height:96px}
#b10 .roles3{display:flex;flex-direction:column;gap:8px}
#b10 .rrow2{display:flex;flex-direction:column;gap:3px;padding:12px 14px;border-radius:12px;border:1px solid var(--line);cursor:pointer}
#b10 .rrow2.on{background:var(--accent-soft);border-color:var(--accent)}
#b10 .rrow2 b{font-family:var(--display);font-weight:600;font-size:17px}
#b10 .rrow2 span{font-size:15.5px;line-height:1.35;color:var(--ink)}
#b10 .pills{display:flex;flex-direction:column;gap:8px;align-items:flex-start;margin-top:14px}
#b10 .pills .pillnote{font-size:14.5px;padding:7px 12px}
/* delivery (roadmap columns) */
#b11 .tl{position:absolute;left:0;top:0;width:1680px;display:grid;grid-template-columns:760px 430px 430px;gap:30px;align-items:stretch}
#b11 .tlbar{grid-column:1/-1;display:grid;grid-template-columns:1220px 430px;gap:30px}
#b11 .tlbar span{position:relative;font-family:var(--display);font-weight:600;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-ink);padding:16px 0 0 18px}
#b11 .tlbar span::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;border-radius:2px;background:var(--accent)}
#b11 .tlbar span::after{content:"";position:absolute;left:0;top:-4px;width:11px;height:11px;border-radius:50%;background:var(--accent)}
#b11 .tlbar span.later{color:var(--muted)}
#b11 .tlbar span.later::before,#b11 .tlbar span.later::after{background:var(--line)}
#b11 .col2{display:flex;flex-direction:column;gap:12px;padding:22px 22px 24px;border-radius:18px;border:1px solid var(--line);background:var(--surface);cursor:pointer}
#b11 .col2.on{box-shadow:0 0 0 3px var(--accent),var(--shadow)}
#b11 .col2 h4{display:flex;align-items:flex-start;gap:10px;font-family:var(--display);font-weight:600;font-size:22px;line-height:1.2}
#b11 .col2 h4 i{width:12px;height:12px;border-radius:50%;background:var(--accent);flex:none;margin-top:8px}
#b11 .col2.trial h4 i{background:var(--trial)}#b11 .col2.later h4 i{background:var(--muted)}
#b11 .ag{align-self:flex-start;font-size:13.5px;font-weight:600;padding:5px 11px;border-radius:999px;background:var(--accent-soft);color:var(--accent-ink);margin-top:-4px}
#b11 .col2.trial .ag{background:var(--trial-soft);color:var(--trial)}#b11 .col2.later .ag{background:var(--line-soft);color:var(--muted)}
#b11 .col2 ul{list-style:none;display:grid;gap:10px;margin-top:4px}
#b11 .col2.launch ul{grid-template-columns:1fr 1fr}
#b11 .col2 li{font-size:16.5px;line-height:1.35;padding:12px 14px;border-radius:12px;background:var(--soft);border:1px solid var(--line-soft)}
#b11 .col2.trial li{background:var(--trial-soft);border-color:transparent}
#b11 .nod{position:absolute;left:0;right:0;bottom:0;font-size:16px;color:var(--muted);text-align:center}
#b11 .col2 .when{display:none;font-family:var(--display);font-weight:600;font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-ink)}
#b11 .col2 .when.later{color:var(--muted)}
/* recommendation */
#b12 .rec{position:absolute;left:0;top:0;width:1060px;height:600px;background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:34px 38px;display:flex;flex-direction:column;gap:16px;box-shadow:var(--shadow)}
#b12 .rec h4{font-family:var(--display);font-weight:700;font-size:34px;line-height:1.15}
#b12 .rec ul{list-style:none;display:flex;flex-direction:column;gap:10px}
#b12 .rec li{display:flex;gap:12px;align-items:center;font-size:20px;padding:11px 14px;border-radius:10px;background:var(--soft);border:1px solid var(--line-soft)}
#b12 .rec .who{margin-top:auto;display:flex;gap:10px;flex-wrap:wrap}
#b12 .rec li i{width:22px;height:22px;border-radius:50%;background:var(--good);flex:none;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.5l3 3 7-7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat}
#b12 .pcard.t{left:1100px;top:0;width:580px;height:300px}
#b12 .pcard.t .im{background-position:center 18%}
#b12 .pcard.u{left:1100px;top:324px;width:278px;height:276px}
#b12 .pcard.v{left:1402px;top:324px;width:278px;height:276px}
/* ===========================================
   PDF MODE
   =========================================== */
@page{size:1920px 1080px;margin:0}
html.pdf,html.pdf body{overflow:visible;height:auto;background:#fff}
html.pdf .deck-viewport{position:static;overflow:visible}
html.pdf .deck-stage{position:static;transform:none!important;width:1920px;height:auto;overflow:visible}
html.pdf .slide{position:relative;display:block!important;visibility:visible!important;opacity:1!important;width:1920px;height:1080px;break-after:page;page-break-after:always;overflow:hidden}
html.pdf .slide *{animation:none!important;transition:none!important}
html.pdf .chrome,html.pdf .hint-legend,html.pdf .toast,html.pdf .info,html.pdf .scrim,html.pdf .infocard{display:none!important}
html.pdf .cue-dot::after,html.pdf .bars .cue{display:none!important}
html.pdf .slide::before{content:attr(data-eyebrow);position:absolute;right:96px;top:44px;font-family:var(--body);font-weight:500;font-size:17px;color:var(--muted)}
html.pdf .pdfmark{position:absolute;left:96px;top:44px;font-family:var(--display);font-weight:700;font-size:16px;letter-spacing:.18em;color:var(--ink)}
html.pdf .slide::after{content:attr(data-credit);position:absolute;left:96px;right:96px;bottom:26px;font-size:15px;color:var(--muted);line-height:1.3;white-space:pre-wrap}
html.pdf .slide.appendix{padding:90px 120px 110px;display:flex!important;flex-direction:column;gap:4px}
html.pdf .slide.appendix h2{font-family:var(--display);font-weight:700;font-size:44px;margin-bottom:10px}
html.pdf .slide.appendix .ap{font-size:18px;line-height:1.45;display:grid;grid-template-columns:520px 1fr;gap:24px;padding:14px 0;border-top:1px solid var(--line-soft)}
html.pdf .slide.appendix .ap b{font-family:var(--display);font-weight:600}
/* ===========================================
   PHONE MODE
   =========================================== */
html.mobile .stagebox,html.mobile .p2{position:static;width:auto;height:auto;margin-top:14px}
html.mobile .p2{border-radius:16px}
html.mobile .strip2{position:static;height:auto;flex-wrap:wrap;gap:10px 16px;padding:12px 14px;font-size:14px}
html.mobile .strip2 .key{margin-left:0;width:100%}
html.mobile .bd{position:static;display:flex;flex-direction:column;gap:16px;padding:14px}
html.mobile .co{display:none}
html.mobile .info{margin-left:8px}
html.mobile .subwrap{display:block;max-width:none}
html.mobile .infocard{width:calc(100% - 32px);max-height:72vh;overflow:auto;padding:20px;position:fixed}
html.mobile .infocard p{font-size:16px}
html.mobile .scrim{position:fixed}
html.mobile .deck-stage{padding-bottom:96px}
html.mobile .pcard{position:relative;left:auto!important;top:auto!important;width:auto!important;height:220px!important;margin-bottom:12px}
html.mobile #t0 .tt{position:static;width:auto;padding:16px 16px 0}
html.mobile #t0 .tt h1{font-size:44px}
html.mobile #t0 .tt p{font-size:17px}
html.mobile #t0 .steps{margin-top:22px;gap:12px;flex-direction:column;align-items:flex-start}
html.mobile #t0 .steps i{display:none}
html.mobile #t0 .card{position:static;transform:none;width:auto;height:auto;margin:20px 16px 0;padding:24px;gap:12px;border-radius:18px}
html.mobile #t0 .card h2{font-size:28px}
html.mobile #t0 .card .pies svg{width:96px;height:96px}
html.mobile #t0 .card .pies .frac{font-size:24px}
html.mobile #t0 .card .q{font-size:18px}
html.mobile #b01 .cards{grid-template-columns:1fr;height:auto;gap:24px}
html.mobile #b01 .ph{height:240px}
html.mobile #b02 .tabs{flex-wrap:wrap;gap:8px;margin-bottom:18px}
html.mobile #b02 .two{grid-template-columns:1fr;gap:20px}
html.mobile #b02 h2{font-size:28px}
html.mobile #b02 .txt p,html.mobile #b02 li{font-size:16px}
html.mobile #b02 .vis{height:auto;min-height:320px}
html.mobile #b02 .v{position:static;padding:16px}
html.mobile #b02 .v.on{display:flex}
html.mobile #b02 .mock{width:100%}
html.mobile #b02 .mock .row{grid-template-columns:1fr}
html.mobile #b05 .cam{padding:64px 0 110px}
html.mobile #b05 .res2{border-left:0;padding-left:0}
html.mobile #b05 .chips{grid-template-columns:repeat(5,1fr)}
html.mobile #b05 .cam{min-height:440px}
html.mobile #b05 .sheet2{width:92%;padding:14px}
html.mobile #b05 .sheet2 .n{flex-direction:column;align-items:flex-start;gap:4px}
html.mobile #b06c .draft,html.mobile #b10 .col + .col{border-left:0;padding-left:0}
html.mobile #b06d .bd{grid-template-columns:1fr}
html.mobile #b06 .sum{grid-template-columns:1fr}
html.mobile #b06 .tr{grid-template-columns:1fr auto;grid-template-areas:"pn b" "hl hl" "dots dots";gap:4px 8px;font-size:14px;padding:8px 10px}
html.mobile #b06 .tr .pn{grid-area:pn}html.mobile #b06 .tr .hl{grid-area:hl;max-width:none;white-space:normal}html.mobile #b06 .flag{flex-direction:column;align-items:flex-start}html.mobile #b06 .tr .dots{grid-area:dots}html.mobile #b06 .tr > b{grid-area:b}
html.mobile #b06 .tr.hd{display:none}
html.mobile #b06 .tr.det{grid-template-areas:none}
html.mobile #b06 .tb{grid-template-columns:120px 1fr 70px}
html.mobile #b06 .ins{border-left:0;padding-left:0}
html.mobile #b06 .tr.det{grid-template-columns:1fr;gap:6px}
html.mobile #b06 .tr.det .items{flex-wrap:wrap}
html.mobile #b06 .tr.det .why{white-space:normal}
html.mobile #b07 .fcards{grid-template-columns:1fr;height:auto;gap:20px}
html.mobile #b07 .fcard{padding:18px;grid-template-columns:1fr;justify-items:center}
html.mobile #b07 .devwrap{width:268px;height:496px}
html.mobile #b07 .fnote{position:static;margin-top:16px;font-size:15px}
html.mobile .phone{width:100%!important;max-width:360px;height:auto!important;min-height:420px}
html.mobile #b07 .dev .phone{min-height:0;height:100%!important}
html.mobile #b09 .grid{grid-template-columns:1fr;margin-top:0}
html.mobile #b09 .arrow2{transform:rotate(90deg);height:40px}
html.mobile #b09 .perm{position:static;margin-bottom:10px}
html.mobile #b11 .tl{position:static;width:auto;grid-template-columns:1fr;gap:14px}
html.mobile #b11 .tlbar{display:none}
html.mobile #b11 .col2 .when{display:inline-flex}
html.mobile #b11 .col2 ul{grid-template-columns:1fr!important}
html.mobile #b11 .nod{position:static;margin-top:6px}
html.mobile #b12 .rec{position:static;width:auto;height:auto;margin-bottom:12px}
html.mobile .gchip .k{font-size:12px}
html.mobile .field{display:block}
html.mobile .field dt{margin-bottom:4px}
html.mobile.capture .chrome.bottom{position:static}
html.mobile .prov,html.mobile .field dt .prov{font-size:12px}
html.mobile .frac{font-size:max(.72em,12px)}
'''
IMCSS = ''.join(f'.im-{k}{{background-image:url("{v}")}}' for k, v in IMG.items())
CHROME_CSS = r'''
/* chrome: light, Codex-style */
.chrome.top{justify-content:space-between}
.chrome.top .lang{position:absolute;left:50%;top:0;transform:translateX(-50%)}
.wordmark{font-family:var(--display);font-weight:700;font-size:16px;letter-spacing:.18em;color:var(--ink);text-transform:uppercase}
.eyebrow{display:inline;font-family:var(--body);font-weight:500;font-size:17px;letter-spacing:0;text-transform:none;color:var(--muted);background:transparent;padding:0;border-radius:0}
.eyebrow::before{display:none}
.chrome.bottom{bottom:22px;height:auto;align-items:flex-end}
.honest-line{font-size:16px;color:var(--muted);line-height:1.3;max-width:560px}
.chrome .right{display:flex;flex-direction:column;align-items:flex-end;gap:8px;max-width:560px}
.credits{font-size:16px;color:var(--muted);line-height:1.3;max-width:560px;text-align:right}
.nav.pill{position:absolute;left:50%;bottom:0;transform:translateX(-50%);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 6px 5px 6px;gap:8px;box-shadow:0 2px 6px rgba(26,31,36,.05)}
.nav.pill .arrow{width:36px;height:36px;border:0;background:transparent}
.nav.pill .arrow:hover{background:var(--line-soft)}
.nav.pill .marks{gap:2px}
.nav.pill .marks button,.nav.pill .marks svg{width:18px;height:12px}
.nav.pill .count{font-size:15px;min-width:64px}
.fs{font-family:var(--body);font-weight:600;font-size:14px;color:var(--ink);background:transparent;border:0;border-left:1px solid var(--line);padding:6px 12px 6px 14px;cursor:pointer;white-space:nowrap}
.fs:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.hint-legend{position:static;left:auto;bottom:auto;display:inline-flex;grid-template-columns:none;align-items:center;gap:8px;font-size:14px;line-height:1.2;white-space:nowrap}
.hint-legend span:last-child{grid-column:auto}
.hint-legend .sep{display:inline-block}
html.mobile .chrome.top .lang{position:static;transform:none}
html.mobile .wordmark{font-size:13px}
html.mobile .eyebrow{font-size:13px;padding:0}
html.mobile .nav.pill{position:static;transform:none;width:100%;border:0;background:transparent;box-shadow:none;padding:0;justify-content:space-between;order:1}
html.mobile .nav.pill .arrow{border:1px solid var(--line);width:44px;height:44px}
html.mobile .fs{display:none}
html.mobile .honest-line{display:none}
html.mobile .chrome .right{display:none}
.mfoot{display:none}
html.mobile .mfoot{display:block;padding:8px 16px 24px;font-size:12.5px;color:var(--muted);line-height:1.35}
html.mobile .mfoot p+p{margin-top:6px}
html.mobile .credits{font-size:12.5px;max-width:none;text-align:left;width:100%}
.tag.quiet{display:none}
'''

# =====================================================================
# markup
# =====================================================================
def img(k, alt=""):
    return f'<div class="im im-{k}" role="img" aria-label="{alt or "Illustrative image, generated"}"></div>'
def head(hkey, skey, ikey):
    return f'''      <div class="head">
        <h1 data-i="{hkey}"></h1>
        <div class="subwrap"><p class="sub" data-i="{skey}"></p><button class="info" type="button" data-info="{ikey}" aria-label="More context"><span>i</span></button></div>
      </div>'''
def strip(keys, key=None, hi=None):
    out = '<div class="strip2">' + ''.join(f'<span class="st2{" hi" if hi == i + 1 else ""}"><i>{i + 1}</i><span data-i="{k}"></span></span>' for i, k in enumerate(keys))
    if key: out += '<span class="key">' + key + '</span>'
    return out + '</div>'
def co(n, left, top, hi=False):
    return f'<span class="co{" hi" if hi else ""}" style="left:{left}px;top:{top}px">{n}</span>'
def frac_svg(shaded, parts, w=150, h=34):
    seg = w / parts; out = f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="6" fill="#fff" stroke="#1A1F24" stroke-width="2"/>'
    for i in range(parts):
        if i < shaded: out += f'<rect x="{1+i*seg}" y="1" width="{seg}" height="{h-2}" fill="#E4A33B"/>'
        if i: out += f'<line x1="{1+i*seg}" y1="1" x2="{1+i*seg}" y2="{h-1}" stroke="#1A1F24" stroke-width="2"/>'
    return out
def phone(inner, foot):
    return f'<div class="phone"><div class="pbar">9:41</div><div class="pbody">{inner}</div><div class="foot" data-i="{foot}"></div></div>'
KEY_AI = '<span><i class="ai"></i><span data-i="keyAi"></span></span><span><i class="me"></i><span data-i="keyMe"></span></span>'

T0 = '''
    <!-- ===== TITLE ===== -->
    <section class="slide active" id="t0" aria-label="Title">
      <div class="tt blk"><div class="k" data-i="t0k"></div><h1 data-i="t0h"></h1><p data-i="t0s"></p>
        <div class="steps"><span class="stp"><b data-i="p1t"></b><span data-i="p1d"></span></span><i></i><span class="stp"><b data-i="p2t"></b><span data-i="p2d"></span></span><i></i><span class="stp"><b data-i="p3t"></b><span data-i="p3d"></span></span></div>
      </div>
      <div class="blk"><div class="card">
        <span class="lbl" data-i="gk"></span>
        <h2 data-i="topic"></h2>
        <div class="pies">
          <svg viewBox="0 0 160 160" width="160" height="160" aria-hidden="true"><circle cx="80" cy="80" r="70" fill="var(--accent-soft)"/><path d="M80 10 A70 70 0 0 1 80 150 Z" fill="var(--accent)"/></svg>
          <span class="frac"><span>1</span><span>2</span></span>
          <span class="frac"><span>1</span><span>4</span></span>
          <svg viewBox="0 0 160 160" width="160" height="160" aria-hidden="true"><circle cx="80" cy="80" r="70" fill="var(--accent-soft)"/><path d="M80 10 A70 70 0 0 1 150 80 L80 80 Z" fill="var(--accent)"/></svg>
        </div>
        <p class="q" data-i="dispQ"></p>
        <span class="status" data-i="chosen"></span>
      </div></div>
    </section>'''

B01 = f'''
    <!-- ===== BEAT 01: who it serves ===== -->
    <section class="slide s23" id="b01" aria-label="Beat 01">
{head('b01h','b01s','b01i')}
      <div class="stagebox blk">
        <div class="cards">
          {''.join(f'<div class="card1" data-p="{i}"><div class="ph">{img(k)}<span class="tag2" data-i="p{i}n"></span></div><b data-i="p{i}t"></b><span data-i="p{i}x"></span></div>' for i, k in ((1, 'teacher'), (2, 'pupils'), (3, 'parent')))}
        </div>
      </div>
    </section>'''

ICONS = [
 '<svg viewBox="0 0 200 96" fill="none" stroke="#127C88" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="40" y="10" width="120" height="76" rx="8"/><path d="M60 34h80M60 50h80M60 66h50"/></svg>',
 '<svg viewBox="0 0 200 96" fill="none" stroke="#127C88" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="30" y="12" width="140" height="56" rx="6"/><path d="M100 68v18M70 86h60"/><path d="M62 40h36M62 52h22" stroke="#E4A33B"/></svg>',
 '<svg viewBox="0 0 200 96" fill="none" stroke="#127C88" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="55" y="8" width="90" height="80" rx="6"/><circle cx="78" cy="34" r="6"/><circle cx="100" cy="34" r="6" fill="#127C88"/><circle cx="122" cy="34" r="6"/><circle cx="78" cy="60" r="6" fill="#127C88"/><circle cx="100" cy="60" r="6"/><circle cx="122" cy="60" r="6"/><path d="M150 20l8 8 16-16" stroke="#2D7A55"/></svg>',
 '<svg viewBox="0 0 200 96" fill="none" stroke="#127C88" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M40 78V40M70 78V24M100 78V52M130 78V16"/><path d="M30 78h130"/><path d="M150 40l20-8-8 20" stroke="#E4A33B"/></svg>',
 '<svg viewBox="0 0 200 96" fill="none" stroke="#127C88" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="70" y="6" width="60" height="84" rx="10"/><path d="M92 14h16"/><path d="M84 40h32M84 54h24M84 68h28" stroke="#E4A33B"/></svg>',
]
B02 = f'''
    <!-- ===== BEAT 02: one topic through the lesson (step section) ===== -->
    <section class="slide s23" id="b02" aria-label="Beat 02">
{head('b02h','b02s','b02i')}
      <div class="stagebox blk">
        <div class="tabs">{''.join(f'<span class="tab{" on" if i == 1 else ""}" data-f="{i}"><i>0{i}</i><span data-i="f{i}"></span></span>' for i in range(1, 6))}</div>
        <div class="two">
          <div class="txt"><span class="eb"><span data-i="stepW"></span> <span id="b02n">01</span> <span id="b02e"></span></span><h2 id="b02dt"></h2><p id="b02dx"></p>
            <ul id="b02ck"><li><i></i><span></span></li><li><i></i><span></span></li><li><i></i><span></span></li></ul>
            <span class="mark" data-i="fkeep"></span>
          </div>
          <div class="vis">
            <div class="v" data-f="1"><div class="mock"><span class="mt" data-i="v1t"></span><span class="mv" data-i="topic"></span><div class="row"><b data-i="v1a"></b><span data-i="v1av"></span></div><div class="row"><b data-i="v1b"></b><span data-i="v1bv"></span></div><div class="pr"><span data-i="optA"></span><span class="prov ai" data-i="provD1"></span></div></div></div>
            <div class="v" data-f="2"><div class="mock disp"><span class="mt" data-i="dispT"></span><span class="mv big" data-i="dispQ"></span><svg viewBox="0 0 420 120" width="420" height="120" aria-hidden="true">{frac_svg(1, 2, 400, 40)}<g transform="translate(0,60)">{frac_svg(1, 4, 400, 40)}</g></svg></div></div>
            <div class="v" data-f="3"><div class="mock"><span class="mt" data-i="v3t"></span><span class="mv" data-i="sheetT"></span><div class="bub2"><em></em><em>A</em><em>B</em><em>C</em><em>D</em>{''.join(f'<span>{n}</span>' + ''.join(f'<i class="{"f" if (n, c) in {(1,2),(2,1),(3,4),(4,2)} else ""}"></i>' for c in range(1, 5)) for n in range(1, 5))}</div><span class="mark" data-i="readMarks"></span></div></div>
            <div class="v" data-f="4"><div class="mock"><span class="mt" data-i="v4t"></span><span class="mv" data-i="topic"></span><div class="bars2"><div><i>5</i><s style="height:50%"></s></div><div><i>6</i><s style="height:60%"></s></div><div><i>7</i><s style="height:70%"></s></div></div><div class="pr"><span class="prov tpl" data-i="flagT"></span><span data-i="sugT"></span></div></div></div>
            <div class="v" data-f="5"><div class="mock"><span class="mt" data-i="v5t"></span><span class="mark" data-i="dgP"></span><div class="row"><b data-i="dgPr"></b><span data-i="dgPrV"></span></div><div class="row hl"><b data-i="dgSh"></b><span data-i="dgShV"></span></div><div class="row"><b data-i="dgAt"></b><span data-i="dgAtV"></span></div></div></div>
          </div>
        </div>
      </div>
    </section>'''

FILLED = {(1,2),(2,1),(3,4),(4,2),(5,3),(6,1),(7,4),(8,2),(9,3),(10,1)}
bub = '<em></em><em>A</em><em>B</em><em>C</em><em>D</em>' + ''.join(f'<span>{n}</span>' + ''.join(f'<i class="{"f" if (n, c) in FILLED else ""}"></i>' for c in range(1, 5)) for n in range(1, 11))
ANS = ['B', 'A', 'D', 'B', 'C', 'A', 'D', 'B', 'C', 'A']
B05 = f'''
    <!-- ===== BEAT 05: pupils on paper (scan pattern) ===== -->
    <section class="slide s23" id="b05" aria-label="Beat 05">
{head('b05h','b05s','b05i')}
      <div class="p2 blk">
        {strip(['st051','st052','st053'])}
        <div class="bd">
          {co(1, 6, 6)}
          <div class="cam" id="cam">
            <span class="hint" id="camHint"></span>
            <div class="sheet2"><span class="t" data-i="sheetT"></span><span class="n"><span data-i="sheetN"></span><s data-i="sheetWho"></s></span><div class="bub">{bub}</div></div>
            <div class="thumb" id="thumb"><b></b><s></s><s></s><s></s></div>
            <span class="shutter2" id="capBtn" role="button" aria-label="Photograph"></span>{co(2, 430, 440)}
          </div>
          <div class="res2"><div class="h4"><span class="tl"><i class="n">3</i><span data-i="resT"></span></span></div>
            <div class="bigread" id="bigread"></div>
            <div class="alabel" data-i="ansLabel"></div>
            <div class="chips">{''.join(f'<span class="ch{" u" if i == 6 else ""}" data-q="{i + 1}"><small>{i + 1}</small>{ANS[i]}</span>' for i in range(10))}</div>
            <div class="rows"><div class="row"><span data-i="matchQ"></span><b data-i="matchV"></b></div><div class="row fixrow"><span data-i="q7"></span><span class="btn small" id="fixBtn" data-i="fixBtn"></span><span class="mark" id="fixed" style="display:none" data-i="fixedBy"></span></div></div>
            <div class="acts"><span class="btn primary" id="confirmBtn" data-i="confirm"></span><span class="status" id="capStatus" style="display:none" data-i="confirmed"></span></div>
          </div>
        </div>
      </div>
      <p class="note blk" style="top:932px;font-size:20px;line-height:1.4" data-i="noDevice"></p>
    </section>'''

NAMES = {'01': 'Aiman Hakim', '02': 'Nurul Aisyah', '03': 'Haziq Iskandar', '04': 'Tan Wei Jie', '05': 'Priya Devi', '06': 'Amirah Zulaikha'}
ROWS = [('01', 's s n s', 'hlN', '7 / 10'), ('02', 's s s s', 'hlOk', '9 / 10'), ('03', 's a n a', 'hlN', '6 / 10'), ('04', 's s s a', 'hlA', '8 / 10'), ('05', 's s n s', 'hlN', '7 / 10'), ('06', 'a s n a', 'hlN', '6 / 10')]
rows = ''.join(f'<div class="tr" data-r="{n}"><span class="pn">{NAMES[n]}</span><span class="hl {h}"><span data-i="{h}"></span></span><span class="dots">' + ''.join(f'<i class="dot {c}"></i>' for c in v.split()) + f'</span><b>{last}</b></div>' for n, v, h, last in ROWS)
TOPICS = [('cvC1', 27, 3, 0), ('cvC2', 25, 4, 1), ('cvC3', 18, 7, 5), ('cvC4', 20, 8, 2)]
tbars = ''.join(f'<div class="tb"><span data-i="{k}"></span><span class="seg"><i class="s" style="flex:{a}"></i><i class="a" style="flex:{b}"></i><i class="n" style="flex:{c}"></i></span><span class="cnt">{a} <em>·</em> {b} <em>·</em> {c}</span></div>' for k, a, b, c in TOPICS)
B06 = f'''
    <!-- ===== BEAT 06: checked answers, class view, assistant (dashboard pattern) ===== -->
    <section class="slide s23" id="b06" aria-label="Beat 06">
{head('b06h2','b06s2','b06i2')}
      <div class="p2 blk">
        {strip(['st061','st062','st063'], key=KEY_AI, hi=3)}
        <div class="bd">
          <div class="cls">
            <div class="h4"><span class="tl"><i class="n">2</i><span data-i="cvT"></span></span><span class="sub2" data-i="rowHint"></span></div>
            <div class="sum">
              <div class="stats"><div class="stat"><b>30</b><span data-i="p2t"></span></div><div class="stat"><b>3</b><span data-i="sumPr"></span></div><div class="stat"><b>6.0<small>/10</small></b><span data-i="sumAvg"></span></div></div>
              <div class="tbars">{tbars}<div class="lg"><span><i class="dot s"></i><span data-i="lgS"></span></span><span><i class="dot a"></i><span data-i="lgA"></span></span><span><i class="dot n"></i><span data-i="lgN"></span></span></div></div>
            </div>
            <div class="tbl"><div class="tr hd"><span data-i="cvP"></span><span data-i="hdH"></span><span data-i="hdT"></span><span data-i="hdL"></span></div>{rows}<div class="tr det" id="pd"></div></div>
          </div>
          <div class="ins"><div class="h4"><span class="tl"><i class="n hi">3</i><span data-i="insT"></span></span></div>
            <div class="flag"><span class="prov tpl" data-i="flagT"></span><span data-i="flag1"></span></div>
            <div class="askT"><span data-i="askT"></span><span class="sub2" data-i="askHint"></span></div>
            <div class="qs"><span class="btn q" data-q="1" data-i="q1"></span><span class="btn q" data-q="2" data-i="q2"></span><span class="btn q" data-q="3" data-i="q3"></span></div>
            <div class="ans" id="ans"></div>
            <div class="acts" id="askActs"><span class="btn aa" data-a="reteach" data-i="actReteach"></span><span class="btn aa" data-a="group" data-i="actGroup"></span><span class="btn aa" data-a="send" data-i="actSend"></span><span class="btn aa" data-a="none" data-i="actNone"></span></div>
            <span class="status" id="askSt" style="display:none"></span>
          </div>
        </div>
      </div>
      <p class="note blk" style="top:932px;font-size:20px;line-height:1.4" data-i="keep6"></p>
    </section>'''

B06C = f'''
    <!-- ===== ADMIN ASSISTANT ===== -->
    <section class="slide s23" id="b06c" aria-label="Admin assistant">
{head('b06ch','b06cs','b06ci')}
      <div class="p2 blk">
        {strip(['st0c1','st0c2','st0c3'], key=KEY_AI, hi=2)}
        <div class="bd">
          <div class="tasks"><div class="h4"><span class="tl"><i class="n">1</i><span data-i="taskT"></span></span><span class="sub2" data-i="taskHint"></span></div>
            {''.join(f'<div class="task{" on" if k == 1 else ""}" data-k="{k}"><b><span data-i="ad{k}"></span><span class="stp" id="tst{k}"></span></b><span class="src" data-i="ad{k}v"></span></div>' for k in (1, 2, 3, 4))}
            <p class="hintt" style="margin-top:auto" data-i="adminNote"></p>
          </div>
          <div class="draft"><div class="to"><span class="h4" style="font-size:22px"><i class="n hi" id="drN">2</i><span data-i="draftT"></span></span><span id="drTo"></span><span class="prov" id="drProv"></span></div>
            <div class="dtext" id="drText"></div>
            <div class="dacts"><i class="n" style="width:30px;height:30px;border-radius:50%;background:var(--ink);color:#fff;font-family:var(--display);font-weight:700;font-size:15px;display:inline-flex;align-items:center;justify-content:center;font-style:normal">3</i><span class="btn primary" id="okBtn" data-i="approve"></span><span class="btn" id="editBtn" data-i="editDraft"></span><span class="btn" id="againBtn" data-i="again"></span><span class="status" id="drSt" style="display:none"></span></div>
            <div class="sentbox"><b data-i="sentT"></b><span><span data-i="sent1"></span><em data-i="sentK"></em></span><span><span data-i="sent2"></span><em data-i="sentK"></em></span></div>
          </div>
        </div>
      </div>
    </section>'''

def device(inner, foot):
    return f'<div class="dev"><div class="phone"><div class="pbar"><span class="notch"></span>9:41</div><div class="pbody">{inner}</div><div class="foot" data-i="{foot}"></div></div></div>'
B06D = f'''
    <!-- ===== DATA: what the app records and gives back (inputs and outputs) ===== -->
    <section class="slide s23" id="b06d" aria-label="Data">
{head('dtH','dtS','dtI')}
      <div class="p2 blk">
        {strip(['st0d1','st0d2','st0d3'], key=KEY_AI, hi=3)}
        <div class="bd">
          <div class="dcol">
            <div class="dcard"><span class="lbl"><i class="n">1</i><span data-i="dtInT"></span></span><div class="chips2"><span data-i="dtIn1"></span><span data-i="dtIn2"></span><span data-i="dtIn3"></span><span data-i="dtIn4"></span><span data-i="dtIn5"></span></div></div>
            <div class="dcard"><span class="lbl"><span data-i="dtWhere"></span></span><p data-i="dtWhereV"></p></div>
            <div class="dcard q"><span class="lbl"><i class="n">2</i><span data-i="dtQT"></span></span><p class="quote" data-i="dtQ"></p><span class="btn primary" id="dtAsk" data-i="dtAsk"></span></div>
          </div>
          <div class="dcol">
            <div class="dcard out"><span class="lbl"><i class="n hi">3</i><span data-i="dtOutT"></span></span><div class="dout" id="dtOut"></div></div>
            <div class="dcard"><span class="lbl" data-i="dtDoneT"></span><ul><li><i></i><span data-i="dtD1"></span></li><li><i></i><span data-i="dtD2"></span></li><li><i></i><span data-i="dtD3"></span></li><li><i></i><span data-i="dtD4"></span></li></ul></div>
            <div class="dcard oc"><span class="lbl" data-i="dtOcT"></span><p data-i="dtOc"></p></div>
          </div>
        </div>
      </div>
    </section>'''

B07 = f'''
    <!-- ===== FAMILIES (two-card pattern) ===== -->
    <section class="slide s23" id="b07" aria-label="Families">
{head('b07h','b07s2','b07i2')}
      <div class="stagebox blk">
        <div class="fcards">
          <div class="fcard"><div class="devwrap">{device('<h4 data-i="dgT"></h4><span class="who" data-i="dgWho"></span><span class="mark" data-i="dgP"></span><div class="sec"><b data-i="dgPr"></b><p data-i="dgPrV"></p></div><div class="sec hl"><b data-i="dgSh"></b><p data-i="dgShV"></p></div><div class="sec"><b data-i="dgAt"></b><p data-i="dgAtV"></p></div><div class="sec"><b data-i="dgAn"></b><p data-i="dgAnV"></p></div>', 'dgNext')}</div>
            <div class="ftext"><b data-i="famP"></b><p data-i="famPs"></p>
            <ul><li><i></i><span data-i="dgSee1"></span></li><li><i></i><span data-i="dgSee2"></span></li><li><i></i><span data-i="dgSee3"></span></li></ul></div>
          </div>
          <div class="fcard"><div class="devwrap">{device('<h4 data-i="myT"></h4><span class="who" data-i="myWho"></span><div class="sec hl"><b data-i="myF"></b><p data-i="myFV"></p></div><div class="sec"><b data-i="myA"></b><p data-i="myAV"></p></div><div class="sec"><b data-i="myOk"></b><p data-i="myOkV"></p></div>', 'agePol')}</div>
            <div class="ftext"><b data-i="famU"></b><p data-i="famUs"></p>
            <ul><li><i></i><span data-i="myF"></span></li><li><i></i><span data-i="myA"></span></li><li><i></i><span data-i="myOk"></span></li></ul></div>
          </div>
        </div>
        <p class="fnote"><span data-i="famYoung"></span> <span data-i="agePol"></span>. <span data-i="dgNot"></span>.</p>
      </div>
    </section>'''

B09 = f'''
    <!-- ===== KOTA BUKU CONTENT ===== -->
    <section class="slide s23" id="b09" aria-label="Content">
{head('b09h','b09s','b09i')}
      <div class="stagebox blk">
        <span class="pillnote trial perm" data-i="pgPerm"></span>
        <div class="grid">
          <div class="page">{co(1, -20, 24)}<span class="ch" data-i="pgT"></span><h4 data-i="pgS"></h4><p data-i="pgB"></p><div class="fig"><svg viewBox="0 0 420 120" width="420" height="120" aria-hidden="true">{frac_svg(1, 2, 400, 40)}<g transform="translate(0,60)">{frac_svg(1, 4, 400, 40)}</g></svg><span data-i="pgFig"></span></div><div class="acts"><span class="chipline" data-i="pgSrc"></span></div></div>
          <div class="arrow2"><svg viewBox="0 0 60 60" width="60" height="60" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M8 30h40M34 16l14 14-14 14"/></svg></div>
          <div class="out">{co(2, -20, 24, hi=True)}<h4 data-i="pgOutT"></h4><div id="pgOut"></div><div class="acts" style="margin-top:auto"><span class="btn primary" id="pgBtn"></span></div></div>
        </div>
      </div>
    </section>'''

B10 = f'''
    <!-- ===== PRACTICAL AND PROTECTED ===== -->
    <section class="slide s23" id="b10" aria-label="Practical and protected">
{head('b10h','b10s2','b10i2')}
      <div class="p2 blk">
        {strip(['st101','st102','st103'])}
        <div class="bd">
          <div class="col"><div class="h4"><span class="tl"><i class="n">1</i><span data-i="a1"></span></span></div><div class="switch" id="netSwitch"><span><span data-i="wifi"></span>: <b id="netSt"></b></span><span class="tog"></span></div><div class="wl"><div class="row"><span data-i="w1"></span><span class="st" data-i="worksOff"></span></div><div class="row"><span data-i="w2"></span><span class="st" data-i="worksOff"></span></div><div class="row"><span data-i="w3"></span><span class="st" data-i="worksOff"></span></div><div class="row need"><span data-i="w4"></span><span class="st" data-i="needsNet"></span></div></div></div>
          <div class="col"><div class="h4"><span class="tl"><i class="n">2</i><span data-i="a2"></span></span></div><ol><li data-i="hs1"></li><li data-i="hs2"></li><li data-i="hs3"></li></ol><div class="h4" style="margin-top:6px" data-i="a3"></div><div class="langs"><span data-i="l1"></span><span data-i="l2"></span><span data-i="l3"></span><span data-i="l4"></span></div><p data-i="acc"></p></div>
          <div class="col"><div class="h4"><span class="tl"><i class="n">3</i><span data-i="roleT"></span></span></div><div class="roles3"><div class="rrow2 on" data-r="1"><b data-i="ro1"></b><span data-i="ro1v"></span></div><div class="rrow2" data-r="2"><b data-i="ro2"></b><span data-i="ro2v"></span></div><div class="rrow2" data-r="3"><b data-i="ro3"></b><span data-i="ro3v"></span></div></div><div class="pills"><span class="pillnote good" data-i="keep10"></span><span class="pillnote" data-i="resid"></span><span class="chipline" data-i="notyet"></span></div></div>
        </div>
      </div>
    </section>'''

B11 = f'''
    <!-- ===== DELIVERY (roadmap columns) ===== -->
    <section class="slide s23" id="b11" aria-label="Delivery">
{head('b11h','b11s','b11i')}
      <div class="stagebox blk">
        <div class="tl">
          <div class="tlbar"><span class="now" data-i="tlNow"></span><span class="later" data-i="tlLater"></span></div>
          <div class="col2 launch on" data-l="1"><span class="when" data-i="tlNow"></span><h4><i></i><span data-i="ln1"></span></h4><span class="ag" data-i="agAll"></span><ul><li data-i="ln1a"></li><li data-i="ln1b"></li><li data-i="ln1c"></li><li data-i="ln1d"></li><li data-i="ln1h"></li><li data-i="ln1e"></li><li data-i="ln1f"></li><li data-i="ln1g"></li></ul></div>
          <div class="col2 trial" data-l="2"><span class="when" data-i="tlNow"></span><h4><i></i><span data-i="ln2"></span></h4><span class="ag" data-i="agSel"></span><ul><li data-i="ln2a"></li><li data-i="ln2c"></li></ul></div>
          <div class="col2 later" data-l="3"><span class="when later" data-i="tlLater"></span><h4><i></i><span data-i="ln3"></span></h4><span class="ag" data-i="agCond"></span><ul><li data-i="ln3a"></li><li data-i="ln3b"></li><li data-i="ln3c"></li><li data-i="ln3d"></li></ul></div>
        </div>
        <p class="nod" data-i="nodates"></p>
      </div>
    </section>'''

B12 = f'''
    <!-- ===== RECOMMENDATION ===== -->
    <section class="slide s23" id="b12" aria-label="Recommendation">
{head('b12h','b12s','b12i')}
      <div class="stagebox blk">
        <div class="rec"><h4 data-i="ask"></h4><ul><li><i></i><span data-i="o1"></span></li><li><i></i><span data-i="o2"></span></li><li><i></i><span data-i="o5"></span></li><li><i></i><span data-i="o3"></span></li><li><i></i><span data-i="o4"></span></li></ul><div class="who"><span class="pillnote" data-i="deliv"></span><span class="pillnote" data-i="tech"></span></div></div>
        <div class="pcard t">{img('teacher')}<div class="cap"><b data-i="p1t"></b><span data-i="p1d"></span></div></div>
        <div class="pcard u">{img('pupils')}<div class="cap"><b data-i="p2t"></b><span data-i="p2d"></span></div></div>
        <div class="pcard v">{img('parent')}<div class="cap"><b data-i="p3t"></b><span data-i="p3d"></span></div></div>
      </div>
    </section>'''

# sample slides: extract, retitle with the draft's headlines, add info buttons
a = s.index('    <!-- ===== SLIDE 1 ===== -->'); b = s.index('    <div class="toast"')
sample = s[a:b]
sample = sample.replace('<section class="slide active" id="s1"', '<section class="slide s23" id="s1"')
for hk, sk, ik in (("h1a","suba","b03i"),("h1b","subb","b03i"),("h1c","subc","b04i")):
    sample, n = re.subn(r'<h1 data-i="%s">[^<]*(?:<[^>]+>[^<]*)*</h1>\s*<p class="sub" data-i="%s">[^<]*</p>' % (hk, sk),
        '<h1 data-i="%s"></h1>\n        <div class="subwrap"><p class="sub" data-i="%s"></p><button class="info" type="button" data-info="%s" aria-label="More context"><span>i</span></button></div>' % (hk, sk, ik), sample)
    assert n == 1, (hk, n)
EXTRA = '\n    <div class="scrim" id="scrim"></div>\n    <div class="infocard" id="infocard" role="dialog" aria-modal="true"><h3 id="infoH"></h3><p id="infoP"></p><button class="close" type="button" id="infoClose" data-i="infoClose"></button></div>\n'
s = s[:a] + T0 + B01 + B02 + sample + B05 + B06 + B06C + B06D + B07 + B09 + B10 + B11 + B12 + EXTRA + s[b:]
rep('.photo{position:absolute;left:120px;top:320px;width:520px;height:620px;', '.photo{position:absolute;left:120px;top:300px;width:520px;height:620px;')
rep('.picker{left:700px;top:320px;width:1100px;height:600px;padding:0}', '.picker{left:700px;top:300px;width:1100px;height:600px;padding:0}')

# chrome
BOTTOM = '''<div class="mfoot"><p data-i="honest"></p><p data-i="credits"></p></div>
    <div class="chrome bottom">
      <p class="honest-line" data-i="honest"></p>
      <div class="nav pill" aria-label="Slide navigation">
        <button class="arrow" id="prev" type="button" aria-label="Previous slide"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.5 4l-6 6 6 6"/></svg></button>
        <div class="marks" id="marks" role="tablist"></div>
        <span class="count" id="count">1 / 15</span>
        <button class="arrow" id="next" type="button" aria-label="Next slide"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.5 4l6 6-6 6"/></svg></button>
        <button class="fs" id="fs" type="button" data-i="fullscreen"></button>
      </div>
      <div class="right">
        <span class="hint-legend" id="hintLegend"><i></i><span data-i="hintLegend"></span><span class="sep"></span><span data-i="hintKey"></span></span>
        <p class="credits" data-i="credits"></p>
      </div>
    </div>'''
s, n = re.subn(r'<span class="hint-legend" id="hintLegend">.*?<div class="chrome bottom">.*?</div>\s*</div>', BOTTOM, s, flags=re.S); assert n == 1, n
TOP = '''<div class="chrome top">
      <span class="wordmark">KOTA BUKU</span>
      <nav class="lang" aria-label="Language">
        <button type="button" data-lang="en" aria-pressed="true">English</button>
        <button type="button" data-lang="ms" aria-pressed="false">Bahasa Melayu</button>
      </nav>
      <span class="eyebrow" data-i="eyebrow"></span>
    </div>'''
s, n = re.subn(r'<div class="chrome top">.*?</nav>\s*</div>', TOP, s, flags=re.S); assert n == 1, n

# sample dictionary corrections (from the reviews)
rep('credits: "<b>Delivered by Sifututor. Powered by Learnest Lab.</b> Kota Buku is the intended proposal context, not an awarded contract. Teacher image is illustrative and generated.",', 'credits: "<b>Delivered by Sifututor. Powered by Learnest Lab.</b> Kota Buku is the intended proposal context, not an awarded contract.",')
rep('credits: "<b>Dihantar oleh Sifututor. Dikuasakan oleh Learnest Lab.</b> Kota Buku ialah konteks cadangan yang dimaksudkan, bukan kontrak yang dianugerahkan. Imej guru adalah ilustrasi yang dijana.",', 'credits: "<b>Dilaksanakan oleh Sifututor. Dikuasakan oleh Learnest Lab.</b> Kota Buku ialah konteks cadangan ini, bukan kontrak yang telah dianugerahkan.",')
rep('h1a: "Start with the <mark class=\\"hl\\">lesson goal</mark>.",', 'h1a: "' + EN['b03h'] + '",')
rep('h1b: "One goal. A plan and practice, <mark class=\\"hl\\">drafted</mark>.",', 'h1b: "' + EN['b03bh'] + '",')
rep('h1c: "Two ways to practise. <mark class=\\"hl\\">One goal</mark>.",', 'h1c: "' + EN['b04h'] + '",')
rep('suba: "The teacher chooses what pupils should learn today. Everything that follows is prepared from that one choice.",', 'suba: "' + EN['b03s'] + '",')
rep('subc: "Both options come from the same lesson goal. The teacher decides which each pupil works on, and can edit either one.",', 'subc: "' + EN['b04s'] + '",')
rep('h1a: "Mulakan dengan <mark class=\\"hl\\">matlamat pelajaran</mark>.",', 'h1a: "' + BM['b03h'] + '",')
rep('h1b: "Satu matlamat. Rancangan dan latihan, <mark class=\\"hl\\">didraf</mark>.",', 'h1b: "' + BM['b03bh'] + '",')
rep('h1c: "Dua cara berlatih. <mark class=\\"hl\\">Satu matlamat</mark>.",', 'h1c: "' + BM['b04h'] + '",')
rep('suba: "Guru memilih apa yang murid perlu pelajari hari ini. Semua yang berikutnya disediakan daripada satu pilihan itu.",', 'suba: "' + BM['b03s'] + '",')
rep('subc: "Kedua-dua pilihan datang daripada matlamat pelajaran yang sama. Guru menentukan pilihan untuk setiap murid, dan boleh mengubah mana-mana satu.",', 'subc: "' + BM['b04s'] + '",')
rep('subb: "I chose the goal. Artificial intelligence drafted the plan and two practice options. I edited one and approved both.",', 'subb: "I chose the goal. The template filled the plan; artificial intelligence drafted two practice options for me to review.",')
rep('subb: "Saya memilih matlamat. Kecerdasan buatan mendraf rancangan dan dua pilihan latihan. Saya mengubah satu dan meluluskan kedua-duanya.",', 'subb: "Saya memilih matlamat. Rancangan diisi secara automatik daripada templat RPH; kecerdasan buatan mendraf dua pilihan latihan untuk saya semak.",')
rep('st2: "Artificial intelligence drafts",', 'st2: "Artificial intelligence drafts practice",')
rep('st2: "Kecerdasan buatan mendraf",', 'st2: "Kecerdasan buatan mendraf latihan",')
rep('planSub: "Drafted from your goal by artificial intelligence. Edit anything.",', 'planSub: "Filled from your goal by the template. Edit anything.",')
rep('planSub: "Didraf daripada matlamat anda oleh kecerdasan buatan. Ubah apa sahaja.",', 'planSub: "Templat RPH diisi berdasarkan matlamat anda. Ubah apa sahaja.",')
rep('provAi1: "AI draft", provAi2: "AI draft",', 'provAi1: "From template", provAi2: "From template",')
rep('provAi1: "Draf AI", provAi2: "Draf AI",', 'provAi1: "Daripada templat", provAi2: "Daripada templat",')
rep('asReq: "Draft a lesson plan and practice options for this goal.",', 'asReq: "Draft practice options for this goal.",')
rep('asReq: "Draf rancangan pelajaran dan pilihan latihan untuk matlamat ini.",', 'asReq: "Draf pilihan latihan untuk matlamat ini.",')
rep('drafting: "Drafting for this goal",', 'drafting: "Preparing for this goal",')
rep('drafting: "Mendraf untuk matlamat ini",', 'drafting: "Menyediakan untuk matlamat ini",')
rep('<div class="field ai"><dt><span data-i="f2k">Success criteria</span><span class="prov ai" data-i="provAi1">AI draft</span></dt>', '<div class="field"><dt><span data-i="f2k">Success criteria</span><span class="prov tpl" data-i="provAi1">From template</span></dt>')
rep('<div class="field ai"><dt><span data-i="f3k">Activities</span><span class="prov ai" data-i="provAi2">AI draft</span></dt>', '<div class="field"><dt><span data-i="f3k">Activities</span><span class="prov tpl" data-i="provAi2">From template</span></dt>')
rep('qM2: "Ali ate {1/2} of a pizza and Mei ate {1/4} of the same pizza. Who ate more? Explain."', 'qM2: "Aiman ate {1/2} of a pizza and Mei Ling ate {1/4} of the same pizza. Who ate more? Explain."')
rep('qM2: "Ali makan {1/2} piza dan Mei makan {1/4} piza yang sama. Siapa makan lebih banyak? Terangkan."', 'qM2: "Aiman makan {1/2} piza dan Mei Ling makan {1/4} piza yang sama. Siapa makan lebih banyak? Terangkan."')
rep('A pizza is cut into 6 slices. Ali eats {2/6}, Mei eats {3/6}. How much is eaten? Explain.', 'A pizza is cut into 6 slices. Aiman eats {2/6}, Mei Ling eats {3/6}. How much is eaten? Explain.')
rep('Sebiji piza dipotong 6 keping. Ali makan {2/6}, Mei makan {3/6}. Berapa yang dimakan? Terangkan.', 'Sebiji piza dipotong 6 keping. Aiman makan {2/6}, Mei Ling makan {3/6}. Berapa yang dimakan? Terangkan.')
rep('hintKey: "R menetapkan semula"', 'hintKey: "R menetapkan semula demo"')
rep('hintLegend: "Titik berdenyut: boleh dicuba"', 'hintLegend: "Titik berdenyut: sentuh untuk mencuba"')
rep('n2: "Rancangan pelajaran"', 'n2: "RPH"')
rep('planTitle: "Rancangan pelajaran anda (RPH)"', 'planTitle: "RPH anda"')
rep('gnote: "Worked example shown for the fractions goal. Other goals get their own drafts."', 'gnote: "Worked example shown for the different-denominators goal. Other goals get their own drafts."')
rep('gnote: "Contoh lengkap dipaparkan untuk matlamat pecahan. Matlamat lain mendapat draf sendiri."', 'gnote: "Contoh lengkap dipaparkan untuk matlamat penyebut berbeza. Matlamat lain mendapat draf sendiri."')
rep('miniSub: "3 pelajaran hari ini. Yang pertama sedia untuk disediakan."', 'miniSub: "3 pelajaran hari ini. Yang pertama boleh disediakan sekarang."')
rep('<title>Start with the lesson goal</title>', '<title>Kota Buku app</title>')
rep('aria-label="Kota Buku app concept, three slides"', 'aria-label="Kota Buku app proposal deck"')
s, n = re.subn(r'deck\.show\(1\)', 'deck.show(deck.slides.findIndex(x => x.id === "s2"))', s); assert n == 1, n
rep('.bubble .who{display:inline;font-size:12px;', '.bubble .who{display:inline;font-size:13px;')
rep('.gchip{position:absolute;left:0;right:0;margin:0 auto;width:max-content;top:282px;', '.gchip{position:absolute;left:0;right:0;margin:0 auto;width:max-content;top:292px;')
rep('.ws{left:160px;top:280px;width:1600px;height:634px;', '.ws{left:160px;top:288px;width:1600px;height:638px;')
# Hafiz, 07/09/2026: the launch boundary lives on the delivery slide and in the i-cards only; slide faces show the full proposed experience
s, n = re.subn(r'\s*<p class="note blk" style="top:930px" data-i="launch">.*?</p>', '', s, flags=re.S); assert n == 1, n
s, n = re.subn(r'\s*<div class="trialbox">.*?</div>', '', s, flags=re.S); assert n == 1, n
rep('.frac{display:inline-flex;flex-direction:column;align-items:center;vertical-align:middle;font-family:var(--display);font-weight:700;line-height:1;margin:0 4px;font-size:.72em}', '.frac{display:inline-flex;flex-direction:column;align-items:center;vertical-align:middle;font-family:var(--display);font-weight:700;line-height:1;margin:0 4px;font-size:max(.72em,13px)}')
rep('.s23 .head{top:98px}', '.s23 .head{top:98px;padding:0 120px}')
rep('.s23 h1{font-size:60px}', '.s23 h1{font-size:48px;line-height:1.1}')
rep('.s23 .sub{font-size:26px;margin-top:16px;max-width:1180px}', '.s23 .sub{font-size:22px;margin-top:12px;max-width:1400px}')
rep('.marks button{width:96px;height:22px;', '.marks button{width:20px;height:12px;')
rep('.marks svg{width:96px;height:22px;display:block}', '.marks svg{width:20px;height:12px;display:block}')
rep('.marks{display:flex;gap:8px;align-items:center}', '.marks{display:flex;gap:3px;align-items:center}')
rep('html.mobile .marks button,html.mobile .marks svg{width:60px;height:16px}', 'html.mobile .marks{display:none}')
rep('.chrome.bottom{bottom:34px;height:48px}', '.chrome.bottom{bottom:26px;height:48px}')
rep('.credits{font-size:15px;color:var(--muted);line-height:1.3;max-width:860px}', '.credits{font-size:15.5px;color:var(--muted);line-height:1.3;max-width:760px}')
rep('.hint-legend .sep{', '.hint-legend .sep{')
rep('.field dt .prov{white-space:normal;line-height:1.25;font-size:13.5px;', '.field dt .prov{white-space:normal;line-height:1.25;font-size:14px;')
rep('  document.getElementById("hintLegend").style.display = Object.keys(u).length >= 8 ? "none" : "";', '')

# dictionaries: merge (JSON-encode values)
def js_obj(d): return ',\n    '.join(f'{json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}' for k, v in d.items())
rep('    after: "The teacher matches each option to a pupil\'s needs. No pupil is labelled, and nothing reaches pupils until the teacher decides.",', '    after: "The teacher matches each option to a pupil\'s needs. No pupil is labelled, and nothing reaches pupils until the teacher decides.",\n    ' + js_obj(EN) + ',')
rep('    after: "Guru memadankan setiap pilihan dengan keperluan murid. Tiada murid dilabel, dan tiada bahan sampai kepada murid sebelum guru memutuskan.",', '    after: "Guru memadankan setiap pilihan dengan keperluan murid. Tiada murid dilabel, dan tiada bahan sampai kepada murid sebelum guru memutuskan.",\n    ' + js_obj(BM) + ',')
order = ['t0h','b01h','b02h','b03h','b03bh','b04h','b05h','b06h2','b06ch','dtH','b07h','b09h','b10h','b11h','b12h']
rep('const TITLES = { en: ["Start with the lesson goal", "One goal, a plan and practice", "Two ways to practise"], ms: ["Mulakan dengan matlamat pelajaran", "Satu matlamat, rancangan dan latihan", "Dua cara berlatih"] };',
    'const TITLES = { en: ' + json.dumps([EN[k] for k in order], ensure_ascii=False) + ', ms: ' + json.dumps([BM[k] for k in order], ensure_ascii=False) + ' };')

# =====================================================================
# JS
# =====================================================================
JS = r'''
/* ===========================================
   DECK: extra state, interactions, info cards, pdf mode
   =========================================== */
const DECK_INIT = { p: 0, f: 1, cap: "done", capOk: false, fix: false, dt: "done", admEdit: false, admText: {}, row: "", ask: 1, askBusy: false, askDec: null, task: 1, adm: { 1: "draft", 2: "draft", 3: "draft", 4: "draft" }, pg: "done", net: false, role: 1, lane: 1 };
Object.assign(state, JSON.parse(JSON.stringify(DECK_INIT)), { tok: 1 });
const NAMES = { "01": "Aiman Hakim", "02": "Nurul Aisyah", "03": "Haziq Iskandar", "04": "Tan Wei Jie", "05": "Priya Devi", "06": "Amirah Zulaikha" };
const PUPILS = { "01": { s: "7 of 10 correct", x: [3, 7, 9], a: [5, 6, 7] }, "02": { s: "9 of 10 correct", x: [7], a: [8, 9, 9] }, "03": { s: "6 of 10 correct", x: [3, 4, 7, 9], a: [5, 5, 6] }, "04": { s: "8 of 10 correct", x: [9, 10], a: [7, 8, 8] }, "05": { s: "7 of 10 correct", x: [3, 7, 9], a: [6, 6, 7] }, "06": { s: "6 of 10 correct", x: [1, 3, 7, 9], a: [5, 6, 6] } };
function renderDeck(){
  const d = T[lang];
  // beat 01
  document.querySelectorAll("#b01 .card1").forEach(c => c.classList.toggle("on", +c.dataset.p === state.p));
  const gchipTxt = document.querySelector('#s3 .gchip [data-i="g3"]'); if (gchipTxt) gchipTxt.textContent = d[state.goal];
  // beat 02
  document.querySelectorAll("#b02 .tab").forEach(c => c.classList.toggle("on", +c.dataset.f === state.f));
  document.querySelectorAll("#b02 .v").forEach(c => c.classList.toggle("on", +c.dataset.f === state.f));
  document.getElementById("b02n").textContent = "0" + state.f; document.getElementById("b02e").textContent = d.of5;
  document.getElementById("b02dt").textContent = d["f" + state.f]; document.getElementById("b02dx").textContent = d["f" + state.f + "d"];
  document.querySelectorAll("#b02ck li span").forEach((el, i) => el.textContent = d["f" + state.f + "c" + (i + 1)]);
  // beat 05
  const cam = document.getElementById("cam"); cam.classList.toggle("read", state.cap === "done");
  document.getElementById("camHint").textContent = state.cap === "busy" ? d.capturing : (state.cap === "done" ? (state.capOk ? d.readyNext : d.readConfirm) : d.capIdle);
  document.getElementById("capBtn").classList.toggle("busy", state.cap === "busy");
  document.getElementById("bigread").textContent = state.cap === "done" ? d.answersRead : d.capturing;
  const fx = document.getElementById("fixBtn"), fxd = document.getElementById("fixed"); fx.style.display = state.fix ? "none" : ""; fxd.style.display = state.fix ? "" : "none";
  const q7 = document.querySelector('#b05 .ch[data-q="7"]'); q7.classList.toggle("u", !state.fix); q7.classList.toggle("ok", state.fix); q7.innerHTML = "<small>7</small>" + (state.fix ? "C" : "D");
  document.getElementById("confirmBtn").style.display = state.capOk ? "none" : "";
  document.getElementById("capStatus").style.display = state.capOk ? "" : "none";
  // beat 06: class view, pupil detail, assistant
  document.querySelectorAll("#b06 .tr[data-r]").forEach(r => r.classList.toggle("on", r.dataset.r === state.row));
  const pd = document.getElementById("pd"), sel = document.querySelector('#b06 .tr[data-r="' + state.row + '"]');
  if (sel) { sel.after(pd); pd.classList.add("show"); } else pd.classList.remove("show");
  const pp = PUPILS[state.row] || PUPILS["01"];
  pd.innerHTML = "<b>" + (NAMES[state.row] || "") + ": " + pp.s.replace("of", d.score.includes("daripada") ? "daripada" : "of").replace("correct", d.score.split(" ").slice(-1)[0]) + "</b><span class=\"items\">" + [1,2,3,4,5,6,7,8,9,10].map(i => "<span" + (pp.x.includes(i) ? " class=\"x\"" : "") + ">" + i + "</span>").join("") + "</span><span class=\"why\">" + d.attempts.replace("5, 6, 7", pp.a.join(", ")) + "</span>";
  document.querySelectorAll("#b06 .q").forEach(b => b.classList.toggle("on", +b.dataset.q === state.ask));
  document.getElementById("ans").innerHTML = state.askBusy ? '<p class="empty pending">' + d.thinking + '</p>' : '<span class="prov ai">' + d.provD1 + '</span><span>' + d["ans" + state.ask] + '</span>';
  document.getElementById("askActs").style.display = state.askBusy || state.askDec ? "none" : "";
  document.querySelectorAll("#b06 .aa").forEach(b => b.classList.toggle("on", b.dataset.a === state.askDec));
  const askSt = document.getElementById("askSt"); askSt.style.display = state.askDec ? "" : "none";
  askSt.textContent = d.decided + ": " + ({ reteach: d.actReteach, group: d.actGroup, send: d.actSend, none: d.actNone }[state.askDec] || "");
  // admin assistant
  const k = state.task, st = state.adm[k], ai = k !== 1;
  document.querySelectorAll("#b06c .task").forEach(t => { const kk = +t.dataset.k; t.classList.toggle("on", kk === k); const p = document.getElementById("tst" + kk); const ss = state.adm[kk]; p.textContent = ss === "ok" ? d.sent : (ss === "busy" ? d.drafting2 : d.waiting); p.className = "stp" + (ss === "ok" ? " ok" : ""); });
  document.getElementById("drTo").textContent = d["ad" + k + "to"]; document.getElementById("drN").classList.toggle("hi", ai);
  const pv = document.getElementById("drProv"); pv.className = "prov " + (ai ? "ai" : "tpl"); pv.textContent = ai ? d.provD1 : d.provAi1;
  const dt = document.getElementById("drText"); dt.className = "dtext " + (ai ? "ai" : "tpl"); if (!state.admEdit) { dt.innerHTML = st === "busy" ? '<span class="empty pending">' + d.drafting2 + '</span>' : (state.admText[k] || d["ad" + k + "d"]); dt.contentEditable = "false"; }
  document.getElementById("editBtn").textContent = state.admEdit ? d.doneEdit : d.editDraft; document.getElementById("editBtn").classList.toggle("on", state.admEdit);
  document.getElementById("okBtn").style.display = st === "draft" && !state.admEdit ? "" : "none"; document.getElementById("editBtn").style.display = st === "draft" ? "" : "none";
  const ag = document.getElementById("againBtn"); ag.style.display = st === "ok" ? "none" : ""; ag.classList.toggle("done", st === "busy");
  const ds = document.getElementById("drSt"); ds.style.display = st === "ok" ? "" : "none"; ds.textContent = d["ad" + k + "s"];
  // data slide
  document.getElementById("dtOut").innerHTML = state.dt === "busy" ? '<p class="empty pending">' + d.dtBusy + '</p>' : '<span class="prov ai">' + d.provD1 + '</span><span>' + d.dtOutV + '</span>';
  document.getElementById("dtAsk").classList.toggle("done", state.dt === "busy");
  // content
  document.getElementById("pgOut").innerHTML = state.pg === "busy" ? '<p class="empty pending">' + d.pgDrafting + '</p>' : '<div class="d"><b>' + d.pgEx + '</b>' + frac(d.pgExV) + '</div><div class="d"><b>' + d.pgDis + '</b>' + d.pgDisV + '</div><div class="d"><b>' + d.pgVoc + '</b>' + d.pgVocV + '</div><span class="prov ai">' + d.provD1 + '</span>';
  const pb = document.getElementById("pgBtn"); pb.textContent = state.pg === "busy" ? d.pgDrafting : (state.used.pg ? d.again : d.pgBtn); pb.classList.toggle("done", state.pg === "busy");
  // practical and protected
  const sw = document.getElementById("netSwitch"); sw.classList.toggle("off", !state.net); document.getElementById("netSt").textContent = state.net ? d.on : d.off;
  document.querySelectorAll("#b10 .wl .row.need").forEach(r => r.classList.toggle("off", !state.net));
  document.querySelectorAll("#b10 .rrow2").forEach(r => r.classList.toggle("on", +r.dataset.r === state.role));
  // delivery
  document.querySelectorAll("#b11 .col2").forEach(l => l.classList.toggle("on", +l.dataset.l === state.lane));
  // cues
  const u = state.used;
  const cue = (sel, on) => document.querySelectorAll(sel).forEach(el => el.classList.toggle("cue-dot", !!on));
  cue("#b01 .card1[data-p='2'] > b", !u.p); cue("#b02 .tab[data-f='2']", !u.f); cue("#capBtn", !u.cap && state.cap !== "busy"); cue("#fixBtn", !state.fix); cue("#confirmBtn", state.fix && !state.capOk);
  cue("#b06 .tr[data-r='05'] .pn", !u.row); cue("#b06 .q[data-q='2']", !u.ask); cue("#b06c .task[data-k='2'] b > span:first-child", !u.task); cue("#okBtn", !u.ok && st === "draft");
  cue("#pgBtn", !u.pg && state.pg !== "busy"); cue("#dtAsk", !u.dt && state.dt !== "busy"); cue("#netSwitch .tog", !u.net); cue("#b10 .rrow2[data-r='2'] b", !u.role); 
  const act = document.querySelector(".slide.active"); document.getElementById("hintLegend").style.display = act && (act.querySelector(".cue-dot") || act.querySelector("#barCue:not([style*=none])")) ? "" : "none";
  // pdf credits per slide
  document.querySelectorAll(".slide").forEach(sl => { sl.setAttribute("data-credit", (d.credits.replace(/<[^>]+>/g, "")) + "\n" + d.honest); sl.setAttribute("data-eyebrow", d.eyebrow); });
}
const wait = (ms, fn) => { const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; const tok = state.tok; setTimeout(() => { if (state.tok !== tok) return; fn(); render(); }, reduce ? 50 : ms); };
document.querySelectorAll("#b01 .card1").forEach(c => c.addEventListener("click", () => { state.p = +c.dataset.p; state.used.p = true; render(); openRolePreview(state.p, c); }));
document.querySelectorAll("#b02 .tab").forEach(c => c.addEventListener("click", () => { state.f = +c.dataset.f; state.used.f = true; render(); }));
document.getElementById("capBtn").addEventListener("click", () => { if (state.cap === "busy") return; state.used.cap = true; state.cap = "busy"; state.capOk = false; state.fix = false; render(); wait(1400, () => { state.cap = "done"; }); });
document.getElementById("fixBtn").addEventListener("click", () => { state.fix = true; state.used.fix = true; render(); });
document.getElementById("confirmBtn").addEventListener("click", () => { if (state.cap !== "done") return; state.capOk = true; render(); });
document.querySelectorAll("#b06 .tr[data-r]").forEach(r => r.addEventListener("click", () => { state.row = state.row === r.dataset.r ? "" : r.dataset.r; state.used.row = true; render(); }));
document.querySelectorAll("#b06 .q").forEach(b => b.addEventListener("click", () => { state.ask = +b.dataset.q; state.askBusy = true; state.askDec = null; state.used.ask = true; render(); wait(1300, () => { state.askBusy = false; }); }));
document.querySelectorAll("#b06 .aa").forEach(b => b.addEventListener("click", () => { state.askDec = b.dataset.a; render(); }));
document.querySelectorAll("#b06c .task").forEach(t => t.addEventListener("click", () => { if (state.admEdit) { state.admText[state.task] = document.getElementById("drText").innerText.trim(); state.admEdit = false; } state.task = +t.dataset.k; state.used.task = true; render(); }));
document.getElementById("okBtn").addEventListener("click", () => { state.adm[state.task] = "ok"; state.used.ok = true; render(); });
document.getElementById("editBtn").addEventListener("click", () => { const el = document.getElementById("drText"); if (state.admEdit) { state.admText[state.task] = el.innerText.trim(); state.admEdit = false; render(); } else { state.admEdit = true; render(); el.contentEditable = "true"; el.focus(); } });
document.getElementById("againBtn").addEventListener("click", () => { const k = state.task; if (state.adm[k] === "busy") return; state.adm[k] = "busy"; render(); wait(1200, () => { state.adm[k] = "draft"; }); });
document.getElementById("dtAsk").addEventListener("click", () => { if (state.dt === "busy") return; state.dt = "busy"; state.used.dt = true; render(); wait(1300, () => { state.dt = "done"; }); });
document.getElementById("pgBtn").addEventListener("click", () => { if (state.pg === "busy") return; state.pg = "busy"; state.used.pg = true; render(); wait(1500, () => { state.pg = "done"; }); });
document.getElementById("netSwitch").addEventListener("click", () => { state.net = !state.net; state.used.net = true; render(); });
document.querySelectorAll("#b10 .rrow2").forEach(r => r.addEventListener("click", () => { state.role = +r.dataset.r; state.used.role = true; render(); }));
document.querySelectorAll("#b11 .col2").forEach(l => l.addEventListener("click", () => { state.lane = +l.dataset.l; state.used.lane = true; render(); }));
/* info cards */
function openInfo(key){ const d = T[lang]; const active = document.querySelector(".slide.active"); const h = active ? active.querySelector("h1") : null; document.getElementById("infoH").textContent = h ? h.textContent : ""; document.getElementById("infoP").textContent = d[key] || ""; document.getElementById("infocard").classList.add("show"); document.getElementById("scrim").classList.add("show"); }
function closeInfo(){ document.getElementById("infocard").classList.remove("show"); document.getElementById("scrim").classList.remove("show"); }
document.querySelectorAll(".info").forEach(b => b.addEventListener("click", e => { e.stopPropagation(); openInfo(b.dataset.info); }));
document.getElementById("infoClose").addEventListener("click", closeInfo); document.getElementById("scrim").addEventListener("click", closeInfo); document.querySelectorAll(".lang button").forEach(b => b.addEventListener("click", closeInfo));
document.addEventListener("keydown", e => { if (e.key === "Escape") closeInfo(); });
/* pdf mode */
function pdfMode(on){
  closeInfo();
  if (on) { Object.assign(state, { cap: "done", capOk: true, fix: true, askDec: "group", adm: { 1: "ok", 2: "ok", 3: "ok", 4: "ok" }, used: { p: 1, f: 1, cap: 1, row: 1, ask: 1, task: 1, ok: 1, pg: 1, net: 1, role: 1, lane: 1 } }); render(); }
  document.documentElement.classList.toggle("pdf", on);
  if (on) { const f = document.documentElement.classList.contains("mobile"); placeAnnotations(); }
  document.querySelectorAll(".slide .pdfmark").forEach(x => x.remove());
  if (on) document.querySelectorAll(".slide").forEach(sl => { const m = document.createElement("span"); m.className = "pdfmark"; m.textContent = "KOTA BUKU"; sl.appendChild(m); });
  if (!on) resetDemo();
  if (on) {
    document.querySelectorAll(".slide.appendix").forEach(x => x.remove());
    const d = T[lang]; const seen = new Set(); const items = [];
    document.querySelectorAll(".slide:not(.appendix)").forEach(sl => { const b = sl.querySelector(".info"); if (!b || seen.has(b.dataset.info)) return; seen.add(b.dataset.info); items.push('<div class="ap"><b>' + sl.querySelector("h1").textContent + "</b><span>" + (d[b.dataset.info] || "") + "</span></div>"); });
    /* pack the notes by measured height: a page takes items until it would overflow */
    const stageEl = document.getElementById("deckStage"); const pagesEl = []; let cur = null;
    const newPage = () => { const sec = document.createElement("section"); sec.className = "slide appendix"; sec.id = "appendix" + (pagesEl.length ? pagesEl.length + 1 : ""); sec.innerHTML = "<h2>" + d.appendix + "</h2>"; sec.setAttribute("data-credit", d.credits.replace(/<[^>]+>/g, "") + "\n" + d.honest); sec.setAttribute("data-eyebrow", d.eyebrow); stageEl.appendChild(sec); pagesEl.push(sec); return sec; };
    cur = newPage();
    items.forEach(html => { cur.insertAdjacentHTML("beforeend", html); if (cur.scrollHeight > cur.clientHeight + 1 && cur.children.length > 2) { cur.lastElementChild.remove(); cur = newPage(); cur.insertAdjacentHTML("beforeend", html); } });
    pagesEl.forEach((sec, i) => { sec.querySelector("h2").textContent = d.appendix + (pagesEl.length > 1 ? " (" + (i + 1) + "/" + pagesEl.length + ")" : ""); });
  } else document.querySelectorAll(".slide.appendix").forEach(x => x.remove());
}
window.pdfMode = pdfMode;
document.getElementById("fs").addEventListener("click", () => { if (document.fullscreenElement) document.exitFullscreen(); else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); });
'''
rep('const MARK = ', JS + '\nconst MARK = ')
rep('  cues();\n  placeAnnotations();\n}', '  cues();\n  renderDeck();\n  placeAnnotations();\n}')
rep('    this.updateTitle();\n    /* re-measure annotations once the entrance motion has settled */', '    this.updateTitle();\n    if (typeof renderDeck === "function") renderDeck();\n    /* re-measure annotations once the entrance motion has settled */')
rep('const pos = el => { const r = el.getBoundingClientRect(); return { x: (r.left - stage.left) / f, y: (r.top - stage.top) / f, w: r.width / f, h: r.height / f }; };', 'const pos = el => { const r = el.getBoundingClientRect(); const base = (el.closest(".slide") || document.getElementById("deckStage")).getBoundingClientRect(); return { x: (r.left - base.left) / f, y: (r.top - base.top) / f, w: r.width / f, h: r.height / f }; };')
rep('  Object.assign(state, { goal: "g3", drafted: true, drafting: false, reviewed: { A: false, B: false }, shade: { half: [true, false], quarter: [true, false, false, false] }, circled: null, editing: null, sheet: { A: "chosen", B: "edited" }, redrafted: { A: false, B: false }, planEditing: false, used: {}, extra: null });',
    '  Object.assign(state, { goal: "g3", drafted: true, drafting: false, reviewed: { A: false, B: false }, shade: { half: [true, false], quarter: [true, false, false, false] }, circled: null, editing: null, sheet: { A: "chosen", B: "edited" }, redrafted: { A: false, B: false }, planEditing: false, used: {}, extra: null, tok: (state.tok || 0) + 1 }, JSON.parse(JSON.stringify(DECK_INIT)));\n  const dtx = document.getElementById("drText"); if (dtx) dtx.contentEditable = "false"; state.admEdit = false; state.admText = {};')

rep('</style>', CSS + IMCSS + CHROME_CSS + '</style>')
import re as _re2
for _a, _b in (('pupils', 'students'), ('Pupils', 'Students'), ('pupil', 'student'), ('Pupil', 'Student')):
    s = _re2.sub(r'(?<![-_\w])' + _a + r'(?![-_\w])', _b, s)
rep('</body>', open(D + 'build/role-previews.html').read() + '\n</body>')
open(D + 'kota-buku-deck.template.html', 'w').write(s)
print("deck template written:", len(s), "chars; slides:", s.count('<section class="slide'))
