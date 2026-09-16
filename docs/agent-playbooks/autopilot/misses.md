# Wrong findings

Every finding a reviewer reported that the verifier disproved. One line each:
the reviewer, the flow, what it claimed, what was actually there.

| Date | Reviewer | Flow | Claimed | Actually |
|---|---|---|---|---|
| 14/09/2026 | Claude | Getting paid | The payout slip has no torn edge; the bottom is a straight line | The bottom edge varies y=768 to y=777 across the width. The teeth are there. The reviewer scanned up from the image bottom and hit the white action bar. |
| 14/09/2026 | Claude | Getting paid | The September chart bar is a different colour with no word explaining it | There was no colour difference. All six bars were bound to the same token, text/primary. The reviewer read `fills[0].color`, which returns a stale raw value on a variable-bound paint. The underlying complaint was still worth acting on: six identical black bars carry no meaning. |
| 14/09/2026 | Codex | Becoming verified | The Malay "IC anda perlu diambil semula" is a literal translation asking for the card, not its photo | The English screen said exactly the same thing, "Your IC needs taking again". Not a Malay defect. Both were reworded. |
| 14/09/2026 | Claude and Codex | Being worth picking | "Verified 18/09/2026" is a future date against a research date of 14/09/2026 | It is the story date both flows use on purpose: sent 14/09, approved 18/09, recorded in becoming-verified.md. A consistent story date is not a defect. Both reviewers measured right and judged wrong. |
| 14/09/2026 | Claude | Being worth picking | The About you row reuses the book-and-pencil that means Education on the sibling hub | Two different assets: writing.png (one open book with a pencil) against education.png (two stacked books). The roughness claim on the camera and calendar in the same finding was right and both were regenerated. |
| 14/09/2026 | Claude | Becoming verified | The two "what you sent" rows go nowhere and are on no not-drawn list | The spec had a round 5 not-drawn entry naming exactly those rows. The reviewer read an older copy. |
| 14/09/2026 | Claude | Becoming verified | The reading object means Documents on the hub and getting paid on screens 10 and 22 | True for screen 10; screen 22 had no objects at all, a different defect the Codex reviewer found. |

## Getting work, round 1 (14/09/2026)

| Reviewer | Finding | Why it was wrong |
|---|---|---|
| Claude | "All six detail screens carry the parent's note" | Screen 09 had none; the 25% case was drawn, only unlisted in Not drawn |
| Claude | Toast rule "places the toast under the safe area at the top" | core-components.md 9 says never at the top; the overlap itself was real |
| Claude | Money icon should come from the Craftwork pack | asset-sources.md: the ringgit is hand-drawn because no pack carries one; the library icon is the approved one |
| Claude | 126pt empty on screen 20 "the same shape" as 07 | 83pt on 20; the fault was real on 07 and 16 |
| Claude | "Most ... 2 days" on screen 16 | Screen 16 has no such sentence; real on 07 and 20 |

## Getting work, round 2 (14/09/2026)

| Reviewer | Finding | Why it was wrong |
|---|---|---|
| Codex | Composite anonymised request rows are invented data | The spec's Known limits records them as real shapes anonymised for a family's address; the profile forbids fabricated numbers, not anonymised ones |
| Claude | The testimonial child "Danish" also on screen 21 | Screen 21 is the empty About you; no testimonial there. The collision on 04, 11 and 16 was real |
| Codex | Cited the area-not-street rule for a missing variant | The missing in-person Chosen page was real; the rule cited is about privacy, not variants |

## Getting work, round 3 (14/09/2026)

No wrong findings. Two taste calls (the empty-list object, the Malay pitch register) went forward as opinions and were taken.

## Getting work, round 4 (14/09/2026)

| Reviewer | Finding | Why it was wrong |
|---|---|---|
| Claude | The spec contradicts itself on the empty-list object | Round 2's dated entry said magnifier; round 3's entry and the table say tray. Revision history, not a live contradiction |
| Claude | Settings and account, round 2: the bell on the Turn on notifications sheet is from a different artwork family, glossy, saturation 0.71 against 0.27 to 0.57 for the pack | bell.png is in the licensed pack folder with its Blender source. Measured across the whole pack, pin 0.71, trophy 0.69 and idea 0.69 sit beside the bell at 0.72; the reviewer sampled the five palest objects and called them the pack |

## Getting work, round 5 and the stack round 1 (14/09/2026)

No wrong findings in either. The stack round's object suggestion (an abacus on a kind-2 empty state) conflicted with patterns.md 12, so a line glyph was used instead; recorded as taken with a change, not as wrong.

## Getting work, the stack rounds 1 and 2 (14/09/2026)

| Reviewer | Finding | Why it was wrong |
|---|---|---|
| Claude | The empty tray on screen 33 repeats screen 12's object | The screen table asks for exactly that, the same meaning on both: nothing has arrived |
| Codex | The Got it box overlaps the round buttons by 8px | They touch, 0 to 1px; the lack of clearance was real, the figure was not |
| Claude | Two counts open with a digit | No such rule existed when raised; it was added to the glossary afterwards |

## Settings and account, rounds 3 and 4 (14/09/2026)

Round 3: no wrong findings. Two judgment calls went forward as opinions and
were both taken, one of them with a different fix: "Your profile is
complete" over four ticked rows was changed, and the full progress bar went
with it, because the heading and the bar measured different things.

| Reviewer | Finding | Why it was wrong |
|---|---|---|
| Codex | Screen 28's area sheet shows a blank list, against patterns.md 9's "never a blank list" | That sentence sits under the no-results state and governs a query that matched nothing. Screen 28 has no query yet. The gap it pointed at was real for a different reason: no screen drew the unfiltered long list, which the other reviewer's B14 finding caught, so 28 now carries it |


## The check itself was wrong, 16/09/2026

`misses.md` has only ever held reviewers' wrong findings. A script can be wrong
the same way, and its findings are more dangerous because they look like
arithmetic.

| Check | Claimed | Actually |
|---|---|---|
| `artwork.figma.py`, first run | 13 images cropped through the object | 9 of the 13 were **photographs**, which fill their box on purpose: the IC shots and the resume pages. A photograph has ink on every edge; an object that can be cut always has at least one clear edge. Exempted by that shape, not by a name list |
| `artwork.figma.py`, second run | The Nakngaji wordmark is cut on its left edge, 34% | A wordmark starts at its first letter, and that letter's stem is tall. Correct work. The check now prints candidates rather than faults, and 4 candidates on 46 images is a small enough review to do by eye |
| `system.figma.py`, contrast | `#4B5563` on a blue ring fails, set it to white | The text sits on the pale wash **inside** the ring, not on the ring. The fix made the screen worse and was reverted. Only a flat surface counts as a background; a ring's bounding box covers text that sits in its hole |
| `system.figma.py`, faint surface | Four blocks are invisible against what is behind them, 1.000:1 | 1.000:1 means the script compared a block with itself. A self-comparison is not a finding |
| `measure.figma.py`, BIG-TEXT | Every chip and pill is too small for its text | The file draws fixed heights the app computes at runtime. The check had no signal at all and was deleted, with the reason written into the script |

**The pattern, and it is the same one as the reviewers':** a bad measurement
usually sits on top of a real complaint. The contrast run that produced the
ring mistake also produced 46 real failures. The artwork run that flagged nine
photographs also found the tray Hafiz had spotted and four screens still
carrying an asset a spec had retired the day before.

**So the rule is not "trust the script".** It is: a script's first run is a
draft. Tighten the exemption until every line it prints is true, then fix. A
check that reports correct work is worse than no check, because the real
findings drown in it.
