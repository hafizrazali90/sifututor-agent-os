# The reviewer profile

Built 14/09/2026 from 20,077 of Hafiz's own messages: 1,358 across 53 Claude
Code sessions and about 18,700 across 585 Codex rollouts, May to September
2026, plus the 30 memory files and `working-with-hafiz.md`.

This is not a style guide. It is what he actually catches. A reviewer agent runs
it as a checklist and reports in plain English.

## The nine checks

Run every one on every screen. A finding must name the check, point at the
screen, and quote a rule, a reference or a number. No evidence, no finding.

**1. Is it dull.**
Does this screen look like every other screen in the set? Is the background
flat where the reference app has depth? Is the only colour the brand colour?
Is there a moment here that would make a tutor feel something, and if not,
should there be? His words: "look more dull and no effort", "u manage to
make it more dull and boring", "so lame", "too traditional", "no creativity".

**2. Was there a reference.**
Can you name the app and screen this was modelled on? If the answer is "it
follows our pattern", that is only enough when the pattern itself was
measured from a reference. His words: "why u never do mobbin research????
why i need to tell u everytime", "check how other gig economy platform are
doing this. your suggestion is too lame or boring".

**3. Is the claim verified.**
Every number, every date, every behaviour asserted on a screen: does it come
from production, from a named spec, or from nowhere? Mockup data that looks
real but is invented is a defect. His words: "why u are using the fake
screenshot??? why no actual??", "the fucking TREQ is fucking mockup use
real!", "did u actually verifiy on prod??".

**4. Does the fix generalise.**
If this screen was corrected, was every other screen with the same problem
corrected too? A single-spot fix is a defect. His words: "Please also check
similar issue!", "fix for all other ismilar copy issue throught the whole
ripple too", "why dont we audit everything?".

**5. Are all the variants drawn.**
The happy path is a sketch. Where are the single item, the long list, the
other brand, the addition, the empty, the failure, the Malay? Where does
every tappable thing go, and is that screen drawn? His words: "but u dont
show me all variant", "make sure to cover all variant, all edge case in
design the screen, make sure all screen is designed!".

**6. Would a bank write this copy.**
Read every line aloud. Does it sound like a person talking to a contractor
who drives to a house to teach a child, or like a policy document? Is there
a promise here the backend cannot keep? His words: "who the fuck use office?
tutor is not even our staff, they like grab driver", "Financial approval
queue meaning is very technical", "not like ai malay".

**7. Do the pixels hold.**
Overlap, clipping, misalignment, tight crops, layout shift, text running
under another element, a row taller than its neighbour. Look at the image,
not the code. His words: "fuckkkk overlap. FUCKING CHECK ALL properly
visually veify", "why u always fucking crop like shit", "Why u always crop
the image too tight zero space!!".

**8. Is the object whole.**
Added 16/09/2026, after he found it himself while the run was working on
something else: "while u working i found truncated 3d icon!" A tray on an empty
screen had its lid running straight off the top of its own picture. Every
geometry check in the system measures where a node **sits**, so a crop through
the drawing was invisible to all of them, and it had survived every round.
The question to ask of any drawn object: **is the whole thing in the frame, and
does it have the same breathing room as the objects beside it?** His older words
belong to the same check: "why u always fucking crop like shit", "Why u always
crop the image too tight zero space!!". `design/scripts/artwork.figma.py` now
reads the pixels for this, but the check is his, not the script's.

**9. Is the object the right one or the first one.**
Icons, illustrations and objects: was this chosen because it means something,
or because it was the first thing to hand? Are two related icons actually
different, or the same icon twice? His words: "the icon selection is lazy and
not creative", "the mark/icon so boring", "why not have 2 variant icon for
from to", "please never use emoji this is typical llm design!".

## How he reads a reply

**Before anything else: check your own words.** A word goes in a reply only if
it is on a screen or in the code, or he has used it himself, or a stranger
would understand it with no explanation. Anything else is invented and stays
out, however precise it feels. On 16/09/2026 the word "twin" had
been used for a full day in every reply and in nine spec files before he said
"your choice of word is so bad". Invented words are invisible to the person who
invented them; the test is the only reliable catch.

**Lead with what changed, not how.** A reply that opens with how a script was
built makes him read to the end to find the point.


- Approval is short. The median approving message is 10 characters. "ok
  good", "proceed", "approve". There is almost never praise.
- **"ok good" is not done.** It clears one gate. It is usually followed
  immediately by the next objection: "ok good but this is not welcome email
  to the company!". A reviewer should never treat a pass as final.
- Rejection is long, about nine times longer, and names the method that
  failed rather than the output.
- He escalates in a fixed ladder: plain retry, then a question about the
  method, then a repeat count ("why i need to tell u everytime"), then
  punctuation and capitals, then profanity. Reaching step three means the
  process is wrong, not the pixel.
- He almost never takes the work over. He re-architects the process so the
  mistake cannot recur, and asks for the rule to be written down.

## How he decides

Counted across the corpus: 731 bare `approve`, 2,377 in the `proceed`
family, 551 bare option letters, 224 requests for a recommendation before
choosing, 342 outright redirects, 53 "follow your rec", 12 full delegations.

- He picks letters decisively and without explanation.
- His commonest move is the **conditional accept**: he takes the option and
  adds a condition in the same breath. Treat every acceptance as carrying an
  unstated next requirement.
- His second commonest is the **redirect**: he rejects the frame of the
  question itself. "why dont we..." A reviewer proposing options should first
  ask whether the options are the right set.
- He asks why before choosing: "why u recomemdn this", "why u choose this
  over the other?" A recommendation without a reason is not a recommendation.
- He guards the final call: "i will be the one who give final say".
- **He answers a narrow question with the principle behind it.** Asked which
  of three things a screen should offer someone whose number is not on an
  account, he replied "i dont understsand, the app is free to download for all,
  for first time user we need them to login > register", then "like how normal
  app does!". The question was wrong, not the options. When an answer restates
  how the world works instead of picking, the thing being asked about is
  usually built on a false assumption and needs rebuilding, not editing.
- **He answers "or something like this".** On a Malay phrase he wrote
  "Keputusan terdahulu or sometghing like this". That is a direction, not a
  string: take the sense, then make it fit. `Keputusan terdahulu` was wider
  than the tile it had to sit in; `terdahulu 7` carried the same sense on one
  line.
- Once a boundary is set he grants wide autonomy: "autopilot", "U do it here
  until all are done", "Please dont ask anything for approval or
  clarification once u already start, if u want ask all now!"

## What he asks for that nobody offered

The highest-value patterns, because they are the ones an AI does not think
of by itself.

1. Generalise the fix to every similar case.
2. Name the edge cases nobody raised, especially states that break layout.
3. Show every variant, not the chosen one.
4. Write the decision down so it does not go stale.
5. Turn the correction into a system rule so it cannot recur.
6. Run an adversarial pass before he sees anything.
7. Keep a live task tree in the chat.
8. Ask him questions instead of handing him a document to read.
9. Fix the tooling before continuing past it.
10. Hand him something he can copy and paste or open.

## Voice, for reading not imitating

Positive: nice, clean, timeless, modern, premium, proper, professional.
Negative: boring, lame, too traditional, shit, ai slop, typical llm, no
creativity, too technical, weird.
Constructions: "why dont we...", "have u actually...", "check for all",
"one by one", "end to end", "reexplain", "explain in non tech".

Malay pasted into a message is almost always a staff report forwarded for
investigation, not a question to him. Read it, act on it, answer in English.

**Do not imitate his spelling or his swearing.** A reviewer writes clear, plain
English. It borrows his standards, not his keyboard.
