# Adversarial review brief for Codex: Kota Buku deck (third build, 07/09/2026)

Read-only. Do not edit any file. Report findings only, in the format at the end.

## What to review

- Deck source: `docs/ai-classroom-concept/production/visual-samples/claude/kota-buku-deck.template.html` (large; the language dictionaries are in the `const T = { en: {...}, ms: {...} }` block near the end; slide markup sits between `<!-- ===== TITLE ===== -->` and `<div class="toast"`; skip the base64 data URIs).
- Built deck: `docs/ai-classroom-concept/production/visual-samples/claude/kota-buku-deck.html` (open in a browser if you can; the language switcher is top centre, arrows navigate, R resets demos).
- Copy source for the twelve beats: `docs/ai-classroom-concept/production/deck-reading-draft.md`.
- Screenshots, desktop, both languages: `docs/ai-classroom-concept/production/visual-samples/claude/screenshots/deck/` (`en-01-t0.png` to `en-15-b12.png`, `bm-01-t0.png` to `bm-15-b12.png`, `en-*-interacted.png`, `en-b06-info.png`, `pdfmode-*.png`, `m-*.png` phone renders).
- PDFs: `kota-buku-deck-en.pdf`, `kota-buku-deck-bm.pdf` in the same folder.

## Rules the deck must obey (each violation is a finding)

1. Beat headlines verbatim from the reading draft in both languages, except that the owner ordered the English word "pupil(s)" replaced by "student(s)" everywhere; treat that substitution as correct and flag any remaining "pupil". Bahasa Melayu keeps "murid". Four slides carry headlines that are not beat headlines by the owner's instruction: the plan slide (s2, a beat 03 body sentence), the class view (b06), the admin assistant (b06c) and the data slide (b06d). Do not flag those four for that reason.
2. No commercial figures, no curriculum codes (DSKP, standard codes), no endorsements or award wording. Credits must read "Delivered by Sifututor. Powered by Learnest Lab." and "Kota Buku is the intended proposal context, not an awarded contract." Fictional names are required in mockups (class 4 Bestari, Cikgu Farah, Aiman Hakim, Nurul Aisyah, Haziq Iskandar, Tan Wei Jie, Priya Devi, Amirah Zulaikha, Danish, Mei Ling); flag any placeholder such as "Pupil 01", "Student 1", "XX" or lorem text.
3. Honesty: one persistent bottom line about concept illustrations, synthetic examples and generated people. By the owner's decision the launch boundary lives only on the delivery slide (b11: launch, guided trial, expansion) and in the "i" context cards; do not flag its absence elsewhere, but flag any slide face that states an unconditional promise (dates, "will", "guaranteed", replacing the report card without approval wording).
4. Teachers-only devices: students never need a device; parents use their own phones; teachers use a supplied iPad. Data residency stays a design requirement, not a certification.
5. No em dashes. Dates DD/MM/YYYY or written out. Spelling "Sifututor".
6. Bahasa Melayu: natural, consistent terminology (RPH, murid, guru, ibu bapa, pecahan); no untranslated English except product names, Wi-Fi, language names and the "Draf AI" label; every key translated with the same meaning.
7. Visual: examine every screenshot in both languages. Flag overlapping or touching elements, clipped text, misaligned rows, inconsistent spacing between siblings, text too small for projection, empty or unbalanced areas, and any slide where the reader cannot tell what to look at first. Compare EN and BM layouts of the same slide.
8. Interaction logic: reset on R, cues, buttons that do nothing, stale text after a language switch, info-card mismatch, PDF states.
9. Consistency with the masters: anything the deck claims that `product-feature-spec.md`, `technical-build-blueprint.md` or the reading draft contradicts (tiers, teacher-only hardware, guided trial at launch, residency).

## Output format

Classify each finding BLOCKING (wrong claim, rule violation, broken layout), MATERIAL (misleading, inconsistent, visibly rough) or MINOR (polish). For each: slide id, language, exact text or element, what is wrong, suggested fix. Quote the text. No praise. End with counts per class. Write the report to `docs/ai-classroom-concept/production/visual-samples/claude/review-codex.md` only if you are running with write access; otherwise print it.
