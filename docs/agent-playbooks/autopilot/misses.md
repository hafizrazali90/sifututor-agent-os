# Wrong findings

Every finding a twin reported that the verifier disproved. One line each:
the twin, the flow, what it claimed, what was actually there.

| Date | Twin | Flow | Claimed | Actually |
|---|---|---|---|---|
| 14/09/2026 | Claude | Getting paid | The payout slip has no torn edge; the bottom is a straight line | The bottom edge varies y=768 to y=777 across the width. The teeth are there. The twin scanned up from the image bottom and hit the white action bar. |
| 14/09/2026 | Claude | Getting paid | The September chart bar is a different colour with no word explaining it | There was no colour difference. All six bars were bound to the same token, text/primary. The twin read `fills[0].color`, which returns a stale raw value on a variable-bound paint. The underlying complaint was still worth acting on: six identical black bars carry no meaning. |
| 14/09/2026 | Codex | Becoming verified | The Malay "IC anda perlu diambil semula" is a literal translation asking for the card, not its photo | The English board said exactly the same thing, "Your IC needs taking again". Not a Malay defect. Both were reworded. |
