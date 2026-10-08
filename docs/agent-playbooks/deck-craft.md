# Deck Craft Playbook

Use this playbook to build, rebuild or repair a slide deck for Hafiz or for a
client to present.

Plain meaning:

```text
Every slide shows its point as a picture: a diagram, a flow, a chart drawn
to scale, a mock screen. Text in boxes is not a slide. A machine checks the
layout, four reviewers check the rest, and Hafiz sees it only after that.
```

This exists because Hafiz rejected two decks in a row as "a wall of text in
boxes" and had to repeat the same corrections each time. The standard comes
from the rebuild of the TNB ILSAS sandbox deck (October 2026). It took four
reviewers from 5.5 to 6.5 out of 10 up to 8.8 to 9 in three rounds.

## Ownership And Boundaries

This playbook owns slide narrative, the graphic chosen for each slide, the
component library, layout checking, the deck review loop and publishing a
deck as a Slides artifact.

- Writing rules and house style for proposals and documents stay with the
  `doc-design` skill. This playbook follows them and does not repeat them.
- A deck that must be edited as PowerPoint uses a native `.pptx` workflow.
  Rendered slides are only a visual reference for it.
- Client deck content (renders, logos, prices) never goes into this
  repository. Keep it in the deck's own folder, and keep client documents in
  Papertrail.

## Tools

The toolkit lives in `.agents/skills/deck-craft/`:

| Path | What it does |
| --- | --- |
| `scripts/lib.py` | Components: header, footer, cards, icon tiles, colour badges, logo chips, flow lines, document chips, numbered dots, strips |
| `scripts/build.py` | Builds slide modules into `project/slides/*.html` and `project/deck.json`, numbers the pages and renders with `--render` |
| `scripts/render_slides.py` | Renders each slide to a 1920x1080 PNG in headless Chrome. Fonts are Geist and Geist Mono (SIL Open Font License), loaded from Google Fonts, or from `~/.cache/deck-craft/fonts.css` when that local copy exists for offline renders |
| `scripts/lint.py` | Geometry lint; exits 1 on any defect (codes below) |
| `scripts/sheet.py` | Contact sheets, four slides each, for judging consistency |
| `scripts/selftest.py` | Proves the toolkit: the example passes and half-empty cards are caught |
| `templates/example/` | A two-slide starter deck: `deck.py` settings, a slide module, `logos.json` |
| `templates/review-brief.md`, `templates/fix-brief.md` | Briefs for reviewers and for fixers |

Start a deck:

```bash
T=~/Projects/Sifututor/.agents/skills/deck-craft
cp -R $T/templates/example <deck folder> && cd <deck folder>
python3 $T/scripts/build.py --render
python3 $T/scripts/lint.py
```

Reference standard: the approved TNB ILSAS sandbox deck, as contact sheets
`all0.png` to `all5.png` in
`~/Projects/proposal-staging/tnb-ilsas-proposal2/deck-v2/png/`. This is
client material, so it is kept on this machine and not in the repository. Read
`DECK-METHOD.md` in the same folder. Look at the sheets before drawing anything.

## Steps

1. **Brief.** Settle who presents, to whom, the decision being asked and the
   voice that follows from that. A client deck presented to its own management
   uses the client's neutral voice: never "we", never selling, and the vendor
   is "the technical partner". Decide the density. A technical proposal is
   dense on purpose; a pitch is not.
2. **Facts first.** Research current facts before technical slides. Every
   number and date comes from one source document. Money goes through ledger
   tokens when a ledger exists (a `tokens.py` with `expand(html)`).
3. **Storyboard.** Write one line per slide: the headline, as a full sentence
   stating the point, and the graphic that proves it, chosen from the menu
   below. Reading only the headlines should tell the story. A slide with no
   graphic is rethought, not decorated.
4. **Build** with the components. Larger decks are split into slide modules
   (about a third of the deck each), one subagent per module, all working
   from one brief made from `templates/fix-brief.md`.
5. **Check every slide yourself.** Render it, look at the PNG, run the lint
   and repeat until it is clean. The lint cannot judge meaning, so looking is
   not optional.
6. **Review loop.** Four reviewers, one lens each, each briefed from
   `templates/review-brief.md` (lenses below). Merge their findings into one
   fix brief and settle any conflicts yourself, writing those decisions into
   the brief. Then fix and run the next round. Each round first re-checks the
   previous round's findings. Stop when no BLOCKER or MAJOR remains; three
   rounds is normal.
7. **Publish.** For a new deck, run the Artifact quickstart and use the Slides
   type. For an existing deck, read it first, then publish by `url`:
   `file_path` is `project/deck.json`, `files` maps each slide and maps
   removed slides to `null`, and `deck.json` never appears in `files` as well.
   Upload logos to the artifact's asset store and keep `blobs.json` (asset id
   to file) and `logos.json` (key to `/_blob/` path) in the deck folder.
8. **Hand over.** Give the link, the scores, what was checked and what was
   not, and what stays open. Copy the deck folder out of the scratchpad to a
   durable place.

## Rules

- Every body slide carries one real graphic. Appendix tables are the only
  exception.
- Fill the canvas to about y=930, keep the 128px side margins and put the
  footer at bottom 64px.
- Text is 24px or larger. No em dashes. Dates are DD/MM/YYYY. Never "Sifu"
  alone.
- Each colour has one meaning across the deck: teal is inside, ok or
  recommended; blue is neutral information; amber is caution or a gate; red is
  blocked or a risk.
- Bars, tracks and timelines are drawn to scale, or drawn so that length
  carries no meaning.
- Logos come only from official assets. Never invent one.
- Honest limits stay on the slide: what is weaker, what is not promised, what
  is not certified.
- One term per thing across slides and notes. Never use one word for two
  things.
- Speaker notes start with "In one sentence:" and end with "If asked:"
  answers. When the answer is not known, the note says it is open and who
  settles it. Every sentence in a note needs a source, just like the slide.
- End with Next steps (owners and outputs), then a closing slide. Open
  questions go in an appendix slide, never as the finale.

## Graphic Menu

| The slide says | Draw |
| --- | --- |
| A request or decision | Stat cards with icon tiles and big numbers, plus a numbered decision panel with deadlines |
| What it does | Mock screens or document panels: file chips, skeleton lines, a "source: p. 12" chip |
| A comparison | Bars to scale against a benchmark, with a tag per bar, plus a short two-column table |
| A process or data path | A left-to-right flow of icon cards joined by flow lines, with a shared store bar between the rows |
| An architecture | Stacked layers inside a dashed boundary, with logo chips on each layer |
| A network boundary | An inside zone, arrows coming in, a numbered list of routes out, and a blocked path with a red cross |
| Threats and controls | Red threat tiles joined by dashed arrows to control cards with right-aligned chips |
| Classes or stages | A gated track: zones with document chips and lock gates showing the condition |
| How success is measured | Gauge bars with threshold ticks, a must-pass group and a traffic-light decision rule |
| A plan | A week grid with bars over it, gate lines with numbered discs and payment markers |
| Who must do what | Swim lanes by owner on a due-date track, plus a people-and-time card |
| Sizes or options | Server drawings with card blocks and capacity meters, or a comparison grid with mini bars and ticks |
| Cost | Stacked bars to scale with the budget band behind them, plus a stop-cost table |
| Risks | A likelihood-by-impact heat map with the codes plotted, plus the top five as cards |
| What happens after | A decision fork: a diamond, elbow lines to Stop, Extend and Go, and the approver for each |
| Next steps | A dated track to scale with numbered dots, above matching step cards |
| Close | A dark slide with the system drawn small and the decision dates as chips |

## Lint Codes

| Code | Meaning |
| --- | --- |
| OUT | Text or a box outside the 128px margins or below y=968 |
| SPILL | Text or a child leaving its box |
| CLIP | Text cut off by nowrap or overflow |
| OVER | Two texts overlapping |
| SMALL | Text under 24px |
| EMPTY | Content ends above y=880 |
| HOLLOW | A card more than 30% empty at the bottom; backdrops with other elements drawn over them, and heat-map cells, are not counted |
| COUNT | More than 200 elements on a slide |

## Slides Format Limits

- One `<section id>` per file, 1920x1080, with inline styles only.
- No `margin` (use gap, padding or absolute positions).
- No `border-style` on its own (write `border:2px dashed #hex`).
- No `<text>` inside svg (put words in positioned `<p>`).
- At most 200 elements per slide. Speaker notes go in an `<aside>`, last.
- `deck.json` is version 4, with `order`, `sections` (each with a start
  slide), `faces` for Geist and `lists: "css"`.

## Review Lenses

| Lens | Checks |
| --- | --- |
| Design | Against the reference standard: a graphic and a focal point, colour meaning, alignment, density, consistency, and any slide that is still boxes |
| Management reader | Understood in 20 seconds; the ask, cost, risk and workload are clear; nothing reads as selling; the notes answer the questions each slide invites |
| Technical and numbers | Every claim, diagram, arrow and bar length against the source document; nothing invented |
| Copy | One term per thing, headlines that state the point, voice, orphan words, dates, numbers that agree across slides, and the shape of the notes |

## What Reviewers Caught That The Lint Did Not

Check these before round 1:

- The same total shown on two different bases on different slides.
- A label touching a card border while it stayed inside its own box.
- A strip drawn to fit its labels instead of its values.
- "outbound: blocked" next to "ten named outbound routes", which contradict
  each other.
- One word naming two things ("gateway", "vendor").
- Dates in the notes not written as DD/MM/YYYY.
- An invented sentence in a speaker note.

## Checks

```bash
python3 .agents/skills/deck-craft/scripts/selftest.py
```

The self-test needs Google Chrome at its standard macOS path.
