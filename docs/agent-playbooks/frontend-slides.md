# Frontend Slides Playbook

Use this playbook to create, convert, redesign, render, or visually check a
self-contained HTML slide presentation.

Plain meaning:

```text
The document workflow decides what is true and what story the deck must prove.
This workflow turns that approved story into a clear, distinctive, reliable
presentation that works in a browser and can be exported locally.
```

## Ownership And Boundaries

This playbook owns:

- slide narrative pacing and density;
- visual-style exploration;
- fixed-stage HTML implementation;
- keyboard, click, touch, and reduced-motion behavior;
- PPTX-to-HTML extraction;
- local rendering, PDF export, and slide-level visual QA.

[document-production.md](document-production.md) remains the source of truth
for stakeholder-document contracts, deep research, evidence maps, claim
registers, blueprint approval, governed drafting, adversarial review, and
publication boundaries.

For an existing native Google Slides deck, use the Google Slides workflow. For
a genuinely editable native PowerPoint deliverable, use a reviewed native
PPTX workflow. Do not present HTML-to-PDF output as an editable PowerPoint.

## Installed Upstream

The visual system is adapted from the MIT-licensed
[`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides)
package at the commit recorded in
`.agents/skills/frontend-slides/UPSTREAM.md`.

The upstream Vercel deployment helper is deliberately excluded. Local deck
creation does not authorise deployment, uploading, publishing, external
sharing, global package installation, or account login.

## Select The Lane

| Lane | Use when | Required route |
| --- | --- | --- |
| New HTML deck | The user wants a new browser presentation. | Brief -> storyboard -> style -> build -> QA -> local handback |
| Stakeholder deck | The deck contains researched, regulated, financial, capability, roadmap, or partner claims. | Document production through approved blueprint -> slide route -> adversarial review |
| PPTX conversion | The user supplies a `.pptx` for conversion to HTML. | Extract -> map -> preserve intent -> rebuild -> compare -> QA |
| HTML enhancement | An existing browser deck needs redesign or repair. | Inspect -> identify invariants -> edit -> regression QA |
| Native PowerPoint | The recipient must edit or forward a `.pptx`. | Use a native PPTX workflow; HTML slides may be a visual reference only. |

## Phase 1: Resolve The Existing Brief

Read the conversation, current document contract, blueprint, governed Markdown,
claim register, brand references, supplied deck, and relevant Koda context.
Do not ask Hafiz to repeat decisions already recorded.

Resolve only what materially changes the deck:

- audience and presentation setting;
- reader-led versus speaker-led use;
- target length or meeting duration;
- required local formats;
- whether the output must be editable as PowerPoint;
- approved brand/style constraints;
- whether the deck is a new build, conversion, or enhancement.

If these are already clear, continue without another questionnaire.

## Phase 2: Build The Assertion Storyboard

Before full visual production, express the deck as ordered slide titles. Each
title should communicate a conclusion, decision, or transition rather than a
topic label. Reading the titles alone should reveal the argument.

For stakeholder decks, the storyboard comes from the approved document
blueprint. Do not create a competing narrative source.

Use one primary message per slide. Split material rather than reducing type or
crowding the stage.

Density choices:

| Mode | Best for | Default behavior |
| --- | --- | --- |
| Speaker-led | Live pitch, keynote, facilitated meeting | Large type, one idea, strong visual, little supporting copy |
| Reading-first | Internal review, leave-behind, async circulation | Self-contained explanation, compact tables or diagrams, stronger annotations |

Use a mixed deck only when the sections have clearly different jobs. Do not
make every slide equally dense.

## Phase 3: Establish The Visual Direction

When no approved house style or reference deck exists, create three genuinely
different single-slide previews. Base them on real deck content and label the
options outside the slides. Never put workflow words such as `preview`,
`template`, or `Option A` into visible slide content.

Use the bundled resources progressively:

1. Read `STYLE_PRESETS.md` and
   `bold-template-pack/selection-index.json`.
2. Shortlist candidates using audience, formality, mood, density, and context.
3. Read only shortlisted `preview.md` files.
4. After selection, read only the selected template's `design.md`.

If Hafiz already approved a visual system, use it directly and skip style
reselection. Existing brand rules and `.claude/skills/doc-design/SKILL.md`
override generic template suggestions for Learnest Lab or Sifututor house
documents unless Hafiz asks for a new direction.

## Phase 4: Build The Deck

Use a fixed 1920 x 1080 slide stage and scale the whole stage uniformly to the
viewport. The content must not reflow into a mobile webpage.

Required behavior:

- one active slide at a time;
- keyboard navigation and visible progress;
- click/touch navigation when appropriate;
- full-screen support where practical;
- `prefers-reduced-motion` support;
- no animation required to understand essential content;
- no scrolling inside a slide;
- no overlap, clipping, hidden footnotes, or unreadably small type;
- offline-safe output when that is part of the document package.

Copy the complete `viewport-base.css` rules into the generated standalone deck
and follow `html-template.md`. Use `animation-patterns.md` selectively. Motion
should support hierarchy and pacing, not distract from evidence.

Use real diagrams, timelines, matrices, flows, and comparisons when they make a
relationship clearer. Decorative cards are not a substitute for information
design.

### Evidence And Citations

For governed decks, every material claim must trace to the document-production
claim register or an approved internal source.

- Render reader-facing sources as real clickable `<a href="...">` links.
- Include enough source identity for a reader to recognise it.
- Keep citations legible in the HTML and static PDF.
- Do not treat a visible plain-text URL as proof that a hyperlink works.
- Do not place sensitive internal evidence in an external-facing deck.
- Distinguish current capability, verified history, approved direction,
  interpretation, and illustrative options.

## Phase 5: Convert Or Enhance Existing Work

For PPTX conversion, use `scripts/extract-pptx.py` only on the supplied local
file. Preserve text, notes, image relationships, ordering, and speaker intent,
then rebuild the presentation as HTML. Conversion is not pixel-perfect unless
that acceptance condition was explicitly agreed and verified.

For HTML enhancement, inspect the existing navigation, stage size, layout
classes, assets, and density before editing. Preserve intentional behavior and
split crowded slides proactively.

Never read `.env*`, secrets, raw credentials, private customer data, or files
under `live/` during conversion or enhancement.

## Phase 6: Local Rendering And Export

The default handback is local HTML plus any explicitly requested local static
format.

Keep output local by default.

Before running `scripts/export-pdf.sh`, inspect the script and environment:

- confirm the target file and output path;
- prefer an already available local Playwright/Chromium installation;
- do not install global packages;
- explain if a temporary dependency or browser download is required;
- keep temporary work outside the repository where practical;
- confirm animations become static final-state visuals in PDF.

Do not run any deployment command or upload the output unless Hafiz separately
authorises the exact target and external action.

## Phase 7: Deterministic And Visual QA

Check every deck, not only a representative sample.

Deterministic checks:

- valid, complete HTML;
- expected slide count and unique slide identifiers;
- one active slide on load;
- no unresolved placeholders or internal workflow labels;
- local assets resolve;
- source links have valid `href` values;
- navigation and progress state are wired;
- reduced-motion behavior exists;
- output files are newer than their governed source.

Visual checks:

- screenshot every slide at 1920 x 1080 or an equivalent 16:9 viewport;
- inspect the montage plus each dense, diagram, table, citation, and closing
  slide at readable size;
- check one smaller desktop viewport and one phone viewport for correct uniform
  scaling and navigation access;
- verify no clipping, overlap, overflow, accidental tiny text, broken images,
  weak contrast, or inconsistent margins;
- open the exported PDF and inspect every page when PDF is part of the output.

For stakeholder or high-stakes decks, route the complete package through the
document-production adversarial review and correct blocking and material
findings before acceptance.

## Acceptance Standard

Do not claim perfection. A locally ready deck means:

```text
The approved storyboard is represented.
Material claims remain governed and traceable.
Every slide was visually inspected.
Navigation, scaling, assets, and links work.
Required local formats were opened and checked.
Blocking findings remaining: 0.
Material findings remaining: 0.
Nothing was deployed, uploaded, committed, or externally shared unless that
boundary was separately approved.
```

## Close-Out

Report:

```text
Status:
Purpose and audience:
Governed source/storyboard:
Generated formats:
Visual system:
Evidence and citations:
Checks performed:
Highest proven state:
Publication/share state:
Recommended next:
Decision needed:
```
