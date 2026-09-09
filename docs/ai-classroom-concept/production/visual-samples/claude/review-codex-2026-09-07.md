# Adversarial Review Report: Kota Buku Deck

## BLOCKING

### 1. Class dashboard is incorrectly placed at launch

- **Slide:** b06
- **Language:** English and Bahasa Melayu
- **Exact text:** “Planned at launch: class view, flags and rule-based suggestions for all teachers.” / “Dirancang ketika pelancaran: paparan kelas, penanda dan cadangan berasaskan peraturan untuk semua guru.”
- **What is wrong:** The product master classifies the teacher-facing class-level dashboard as Fast-follow. The reading draft explicitly says Beat 06 must use a per-student, explainable suggestion and “not a generative narrative or Fast-follow class-wide dashboard.” This slide presents the class dashboard as available to every teacher at launch.
- **Suggested fix:** Rebuild b06 around one student’s answers, practice record and rule-based next-step decision. Move the class-wide dashboard to the expansion lane or label the entire class-view surface Fast-follow.

### 2. The assistant is incorrectly placed in a guided trial at launch

- **Slide:** b06 and b06c
- **Language:** English and Bahasa Melayu
- **Exact text:** “Plain-language analysis and the assistant through a guided trial for selected teachers.” / “Analisis bahasa mudah dan pembantu melalui percubaan berpandu untuk guru terpilih.”
- **What is wrong:** The product master places the AI-generated narrative and chat-based teaching assistant in Fast-follow. The reading draft reserves the guided trial at launch for full AI-drafted RPH only. The deck invents an additional launch-time guided trial for the analytics and administrative assistant.
- **Suggested fix:** Present only rule-based, traceable per-student suggestions at launch. Move plain-language AI analysis and assistant conversation to Fast-follow/expansion.

### 3. The data slide brings Fast-follow outputs into the launch build

- **Slide:** b06d
- **Language:** English and Bahasa Melayu
- **Exact text:** “What comes back at launch: a progress record for every student by topic, a class report for the school, and the parent summary.” It also says: “Through the guided trial with selected teachers: targeted practice drafted by the assistant from a student’s own wrong answers, and plain-language reports.”
- **What is wrong:** A class-level reporting surface and plain-language AI narrative are Fast-follow in the product master. Automatic history-based, per-student differentiated material is also Fast-follow in the reading draft and feature specification. Describing these outputs as launch or launch-time guided-trial capabilities contradicts the approved tiers.
- **Suggested fix:** Keep launch outputs to per-student progress records, teacher-confirmed rule-based suggestions and curated parent summaries. Move class reports, AI-authored reports and history-driven targeted practice to expansion.

### 4. The delivery slide contradicts the approved delivery boundary

- **Slide:** b11
- **Language:** English and Bahasa Melayu
- **Exact elements:** “Class view, flags and rule-based suggestions” in the all-teachers launch lane; “Plain-language analysis and the teacher’s assistant” in the guided-trial-at-launch lane.
- **What is wrong:** The class dashboard and class-wide patterns are Fast-follow, and the assistant is Fast-follow. The reading draft defines the guided-trial lane solely as full AI-drafted lesson plans for selected teachers. This is the deck’s designated delivery-boundary slide, so the contradiction changes the proposal’s commitment.
- **Suggested fix:** Remove “Class view” from launch, retaining per-student records and rule-based support suggestions. Remove the assistant from the guided-trial lane. Put class-level analysis and the assistant in expansion.

### 5. Obsolete screenshots retain prohibited “pupil” wording and a stale 14-slide sequence

- **Slides:** b02, b07, b09, b10, b11 and b12
- **Language:** English; stale sequencing also affects Bahasa Melayu
- **Exact files/elements:**
  - `en-b02-step2.png`: “pupils work on paper” and “Practice printed for pupils,” count `3 / 14`
  - `en-10-b07.png`: “older pupils,” count `10 / 14`
  - `en-11-b09.png`: “Two pupils…,” count `11 / 14`
  - `en-12-b10.png`: “pupil data,” count `12 / 14`
  - `en-13-b11.png`: “Parent and pupil summaries,” count `13 / 14`
  - `en-14-b12.png`: “pupil learning” and “Pupils,” count `14 / 14`
  - The corresponding `m-en-10-b07.png` through `m-en-14-b12.png` retain the same obsolete terminology and counts.
  - `bm-10-b07.png` through `bm-14-b12.png` and `m-bm-13-b11.png` also belong to the obsolete 14-slide sequence.
- **What is wrong:** Rule 1 requires every visible English “pupil” to be replaced with “student.” The review bundle also contains two conflicting numbered sequences for the same later slides, making it unclear which screenshots constitute the deliverable.
- **Suggested fix:** Delete every obsolete 14-slide render and regenerate all baseline, interaction and mobile screenshots from the current 15-slide build.

### 6. Fixed mobile chrome obscures slide content

- **Slides:** Global mobile layout, t0 through b12
- **Language:** English and Bahasa Melayu
- **Exact element:** Fixed bottom block containing the honesty line, navigation, slide count and credits.
- **What is wrong:** In the full-page mobile captures, the fixed block sits across the active content instead of reserving space for it. It cuts through photographs, cards, tables, controls and explanatory text on nearly every mobile slide. The most consequential examples include b05’s capture workflow, b06’s class table, b06c’s task/draft area and b11’s first delivery lane.
- **Suggested fix:** Make the mobile chrome part of normal flow, create a compact collapsible control bar, or reserve viewport space so content never passes underneath it. Regenerate every mobile screenshot afterward.

### 7. The mobile information dialog is visibly clipped

- **Slide:** b06
- **Language:** English
- **Exact file/element:** `m-en-b06-info.png`; the information-card paragraph is cut off at the viewport bottom and the Close button is not initially visible.
- **What is wrong:** The interaction state does not present a complete dialog. The user must discover an unindicated nested scroll before reaching the dismissal control, while the underlying fixed chrome competes with the modal.
- **Suggested fix:** Constrain the dialog within the unobscured viewport, keep its title and Close button sticky, provide a visible scroll region for the body, and hide the mobile bottom chrome while a modal is open.

### 8. The admin “Edit” action discards the edit

- **Slide:** b06c
- **Language:** English and Bahasa Melayu
- **Exact element:** “Edit” / “Ubah”
- **What is wrong:** The button merely sets the draft element to `contentEditable`. There is no Done or Save transition and no state captures the edited text. Pressing “Approve and send,” changing tasks, redrafting, switching language or invoking another render restores the dictionary copy and loses the user’s change. The control therefore does not complete the action it advertises.
- **Suggested fix:** Store edited text per task, add a visible Done/Save state, and ensure approval uses the stored edited value. Verify persistence across task selection and language changes and clearing on `R`.

### 9. The fictional student changes class between slides

- **Slide:** b07, with conflict against b05
- **Language:** English and Bahasa Melayu
- **Exact text:** “Nurul Aisyah, 2 Amanah” versus “Nurul Aisyah, 4 Bestari”
- **What is wrong:** The same named student is shown in two different classes. Rule 2 specifies 4 Bestari as the fictional class used by the mockups.
- **Suggested fix:** Change b07 to “Nurul Aisyah, 4 Bestari” in both dictionaries and regenerate the desktop, mobile and PDF outputs.

### 10. A synthetic notice contains an unconditional “will” promise

- **Slide:** b06c
- **Language:** English and Bahasa Melayu
- **Exact text:** “We will share the class’s progress in fractions and the next topics.” / “Kami akan berkongsi kemajuan kelas dalam pecahan dan topik seterusnya.”
- **What is wrong:** Rule 3 explicitly requires unconditional “will” wording on a slide face to be flagged. Although this is synthetic message content, it still appears as proposal-facing copy without qualification.
- **Suggested fix:** Replace it with a factual agenda formulation, such as “The meeting agenda includes the class’s progress in fractions and the next topics.”

## MATERIAL

### 11. Interaction toast covers a core device-boundary statement

- **Slide:** b05
- **Language:** English
- **Exact file/element:** `en-b05-interacted.png`; toast “Confirmed by the teacher” over “No student needs a device to take part.”
- **What is wrong:** The confirmation state hides one of the deck’s mandatory teacher-only-device messages.
- **Suggested fix:** Move the toast above the bottom note or place it in a reserved notification area that never covers slide copy.

### 12. Persistent compliance and credit text is too small for projection

- **Slides:** Global
- **Language:** English and Bahasa Melayu
- **Exact elements:** The concept/synthetic/generated-people honesty line and the delivery/proposal-context credits.
- **What is wrong:** These lines are rendered at approximately 15–15.5 px on a 1920-wide stage and become smaller when the deck is scaled to common display resolutions. They contain material qualification and contract-status language but are not reliably readable from a room.
- **Suggested fix:** Increase the projected size and contrast, shorten the phrasing if necessary, and reserve enough footer height to keep both statements legible.

### 13. Dense mockup text is below practical projection size

- **Slides:** b06, b06c, b06d and b07
- **Language:** English and Bahasa Melayu
- **Exact elements:** Class-table headings and row hints, task-source labels, status pills, data chips, output lists and text inside the two family phone mockups.
- **What is wrong:** Much of the operational detail is approximately 13–16 px within a 1920-wide slide. It is readable only as a close desktop artifact, not as projected presentation content. Important distinctions such as rule-based versus AI draft and teacher approval become too quiet.
- **Suggested fix:** Remove secondary details, enlarge the remaining labels, and use progressive interaction or separate detail slides instead of fitting complete application screens onto one projected slide.

### 14. The mobile class table truncates the information needed to understand it

- **Slide:** b06
- **Language:** English and Bahasa Melayu
- **Exact element:** Four-column student table in `m-en-08-b06.png` and `m-bm-08-b06.png`.
- **What is wrong:** Headline and topic content collapses into very narrow columns with ellipses and extremely small labels. The reader cannot reliably connect a student, topic and status, undermining the slide’s primary visual.
- **Suggested fix:** Replace the mobile table with stacked student cards or show only student, primary flag and an expandable detail section.

### 15. Bahasa Melayu action expansion breaks the b06 button layout

- **Slide:** b06
- **Language:** Bahasa Melayu
- **Exact element:** “Bukan sekarang”
- **What is wrong:** The longer translated action wraps onto a second row at the bottom of the assistant panel and sits against the panel boundary. The English actions remain a coherent row, so the language switch materially changes the balance and finish.
- **Suggested fix:** Use a two-by-two action grid in both languages, shorten the BM label where appropriate, or increase the action area’s reserved height.

### 16. The mobile delivery headers become detached from their lanes

- **Slide:** b11
- **Language:** English and Bahasa Melayu
- **Exact elements:** “At launch” followed by “Later, when conditions are met” before the stacked launch, guided-trial and expansion cards.
- **What is wrong:** Desktop column headers are flattened into a single vertical sequence on mobile. The “Later” heading appears before the launch and guided-trial content it does not govern, making the sequence misleading.
- **Suggested fix:** Place a timing heading directly above each corresponding mobile lane, or hide the desktop timeline bar and add timing labels inside each stacked card.

### 17. Bahasa Melayu template wording is mechanical and unnatural

- **Slides:** b02 and s2
- **Language:** Bahasa Melayu
- **Exact text:** “Rangka mengisi rancangan,” “Diisi daripada matlamat anda oleh rangka,” and “Pilih topik; rangka mengisi rancangan…”
- **What is wrong:** “Rangka” is treated as an acting subject that “fills” the plan, producing literal and awkward Malay. The intended meaning is that the RPH template is populated using the selected learning goal.
- **Suggested fix:** Use natural constructions such as “Rancangan diisi secara automatik berdasarkan matlamat,” “Templat RPH diisi berdasarkan matlamat anda,” and “Pilih topik; aplikasi mengisi templat RPH…”

### 18. “Pandangan” is not a natural translation of “Insights” in this interface

- **Slide:** b06
- **Language:** Bahasa Melayu
- **Exact text:** “Pandangan”
- **What is wrong:** In this analytics context, “Pandangan” reads as a view or opinion, not a set of findings derived from class records.
- **Suggested fix:** Use “Dapatan,” “Cerapan,” or another terminology choice validated with the rest of the product’s BM vocabulary.

## MINOR

### 19. The mobile RPH field layout gives labels too much width

- **Slide:** s2
- **Language:** English and Bahasa Melayu
- **Exact elements:** “Success criteria” / “Kriteria kejayaan” and their corresponding field values.
- **What is wrong:** The label/value treatment leaves a narrow value column, forcing short sentences into excessive line wrapping and making the card unnecessarily tall and visually uneven.
- **Suggested fix:** Stack field labels above their values in mobile mode and allow the value to use the full card width.

## Counts

- **BLOCKING:** 10
- **MATERIAL:** 8
- **MINOR:** 1
- **TOTAL:** 19