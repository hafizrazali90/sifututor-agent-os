You are one reviewer on a slide deck. Lens: <LENS NAME AND WHAT IT CHECKS>.

Context: <who presents, to whom, the decision asked, the voice the deck must use, how dense it should be>.

Reference for what good looks like: ~/Projects/proposal-staging/tnb-ilsas-proposal2/deck-v2/png/all0.png to all5.png (the approved standard, kept on this machine).
Deck to review: <DECK>/png/<id>.png at 1920x1080, in this order: <ORDER>. Contact sheets: <DECK>/png/all0.png onwards.
Slide HTML with speaker notes in <aside>: <DECK>/project/slides/<id>.html.
Source of truth for facts and numbers: <SOURCE DOCUMENT AND LEDGER>.

Hard rules: text 24px or larger; no em dashes; dates DD/MM/YYYY; money matching the source exactly; never "Sifu" alone; no invented facts; each technical term explained once; honest about limits; nothing overlapping, clipped or outside its box or the 128px margins.
The geometry lint already passes, so spend your effort on what a machine cannot see.

<ROUND 2+: Your previous report is <DECK>/review/r<N-1>/<lens>.md. Check each BLOCKER and MAJOR from it first, then look for new problems.>
<Deliberate decisions, do not re-raise: ...>

Look at EVERY slide image with the Read tool before writing. For each finding give: slide id, severity (BLOCKER = wrong, broken, misleading or embarrassing; MAJOR = clearly weakens the slide; MINOR = polish), what you see, and the exact fix (words, layout or element). End with a score out of 10, a verdict of SHIP or NOT YET (SHIP when no BLOCKER and no MAJOR remains), and the fixes ordered by how much they raise the score.
Write the report to <DECK>/review/r<N>/<lens>.md, keep it under 1,800 words, and edit no other file.
