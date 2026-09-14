# Wrong findings

Every finding a twin reported that the verifier disproved. One line each:
the twin, the flow, what it claimed, what was actually there.

| Date | Twin | Flow | Claimed | Actually |
|---|---|---|---|---|
| 14/09/2026 | Claude | Getting paid | The payout slip has no torn edge; the bottom is a straight line | The bottom edge varies y=768 to y=777 across the width. The teeth are there. The twin scanned up from the image bottom and hit the white action bar. |
| 14/09/2026 | Claude | Getting paid | The September chart bar is a different colour with no word explaining it | There was no colour difference. All six bars were bound to the same token, text/primary. The twin read `fills[0].color`, which returns a stale raw value on a variable-bound paint. The underlying complaint was still worth acting on: six identical black bars carry no meaning. |
| 14/09/2026 | Codex | Becoming verified | The Malay "IC anda perlu diambil semula" is a literal translation asking for the card, not its photo | The English board said exactly the same thing, "Your IC needs taking again". Not a Malay defect. Both were reworded. |
| 14/09/2026 | Claude and Codex | Being worth picking | "Verified 18/09/2026" is a future date against a research date of 14/09/2026 | It is the story date both flows use on purpose: sent 14/09, approved 18/09, recorded in becoming-verified.md. A consistent story date is not a defect. Both twins measured right and judged wrong. |
| 14/09/2026 | Claude | Being worth picking | The About you row reuses the book-and-pencil that means Education on the sibling hub | Two different assets: writing.png (one open book with a pencil) against education.png (two stacked books). The roughness claim on the camera and calendar in the same finding was right and both were regenerated. |
| 14/09/2026 | Claude | Becoming verified | The two "what you sent" rows go nowhere and are on no not-drawn list | The spec had a round 5 not-drawn entry naming exactly those rows. The reviewer read an older copy. |
| 14/09/2026 | Claude | Becoming verified | The reading object means Documents on the hub and getting paid on boards 10 and 22 | True for board 10; board 22 had no objects at all, a different defect the Codex twin found. |

## Getting work, round 1 (14/09/2026)

| Twin | Finding | Why it was wrong |
|---|---|---|
| Claude | "All six detail boards carry the parent's note" | Board 09 had none; the 25% case was drawn, only unlisted in Not drawn |
| Claude | Toast rule "places the toast under the safe area at the top" | core-components.md 9 says never at the top; the overlap itself was real |
| Claude | Money icon should come from the Craftwork pack | asset-sources.md: the ringgit is hand-drawn because no pack carries one; the library icon is the approved one |
| Claude | 126pt empty on board 20 "the same shape" as 07 | 83pt on 20; the fault was real on 07 and 16 |
| Claude | "Most ... 2 days" on board 16 | Board 16 has no such sentence; real on 07 and 20 |

## Getting work, round 2 (14/09/2026)

| Twin | Finding | Why it was wrong |
|---|---|---|
| Codex | Composite anonymised request rows are invented data | The spec's Known limits records them as real shapes anonymised for a family's address; the profile forbids fabricated numbers, not anonymised ones |
| Claude | The testimonial child "Danish" also on board 21 | Board 21 is the empty About you; no testimonial there. The collision on 04, 11 and 16 was real |
| Codex | Cited the area-not-street rule for a missing variant | The missing in-person Chosen page was real; the rule cited is about privacy, not variants |

## Getting work, round 3 (14/09/2026)

No wrong findings. Two taste calls (the empty-list object, the Malay pitch register) went forward as opinions and were taken.
