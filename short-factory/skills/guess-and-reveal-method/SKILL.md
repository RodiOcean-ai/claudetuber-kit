---
name: guess-and-reveal-method
description: Build a short-factory Short (or its idea, first line, beat sheet, reveal moment, ending or title check) with the measured guess-and-reveal recipe from our study of a top science Shorts channel, turned into a 30-second faceless 3D Short - a real-looking object already about to do something on frame one, the viewer's own guess set up in one line, a visible wait-and-see beat (a countdown, a hand on the rope, a foot over the water) instead of a spoken tease, the guess broken ON SCREEN so the "But" happens in the picture, the voice never talking over the surprise, the hero's own body at stake, a side character reacting, an ending on the "no way" that pays the title's promise, and no question-only hooks. Use whenever the owner says "guess and reveal", "show don't tell", "make them guess", "prediction", "the guess fails on screen", "wait and see", "countdown", "tension not tease", "don't talk over the reveal", "let it breathe", "silent beat", "body at stake", "explained vs jumped in", "the shade balls one", "science Short", "reveal check", or when sf-pipeline writes the script (stage 3) or plans the 3D reveal (stage 5) for any "How did X get Y?" episode whose middle explains instead of shows.
---

# Guess-and-reveal method: let the viewer guess, make them wait, break the guess on screen

Learned from our study of 15 Nov 2026: the studied science channel's top 10 Shorts (24M-64M), 3 weak 2026 Shorts (0.39M-0.69M), all 97 Shorts titles and its top 10 long videos. Evidence: `${CLAUDE_PLUGIN_ROOT}/reference/creators/guess-and-reveal/SECRET_SAUCE.md`. Numbers: `STUDY.md`, `techniques.md`, story chart `story_blocks.png` in the same folder.

**Copy the craft, never the identity:** no face, name, voice, catchphrases, real footage, lab or locations of the studied creator. No borrowed clips, screenshots or thumbnails. Faceless toy figures only; the creator stays anonymous until the last line (`reference/lessons.md`).

**Claude builds, the owner clicks.** This skill is free: ideas, scripts, beat sheets and Blender plans. Voice and image generation follow the money rules in `reference/lessons.md`.

**The format benchmark keeps the final word on format.** The studied channel's 58 s, 140 words, silent stretches of 5-17 s, hard cuts, voice only 10 LU over the music and no loop do not apply. The shorts-format rule wins: 27-35 s, 75-95 words, about 2.8 words/s, voice on frame one, no pause over 0.5 s, voice about 16 LU above the music, flights, loop to frame one.

## The recipe (why the hits win, in the viewer's head)
1. **Frame one is a real-looking thing about to do something** (7 of 10 hits, 0 of 3 weak). Not a face, a map, a chart or a cartoon idea. The eye gets a question before the ear gets a word. In our lab: the object fills the phone and is already moving.
2. **The viewer makes the guess.** One line (or one picture) sets up the obvious prediction: "you'd get wet", "they'd land together", "he'd sink". The viewer has lived it, so they guess without being asked.
3. **A visible wait, never a spoken tease** (tension 8 of 10 hits vs 0 of 3 weak; tease 0 of 10 vs 2 of 3). A countdown, a hand on the rope, a foot over the water. Never "and the answer will surprise you" or "there's a catch".
4. **The guess breaks on screen** (6 of 10 vs 0 of 3). The "But" is something we SEE: he steps out dry, the ladder falls faster, the weight goes up. If the voice has to say the surprise, it isn't one.
5. **Never talk over the surprise** (silent 4.7 s+ in 4 of 10 hits, 0 of 3 weak; voice covers 76 % vs 90-93 %). For us, inside the shorts-format 0.5 s rule: the line before the reveal ends, the reveal lands on its own real sound in the gap, the next line comments on it.
6. **Something to lose** (5 of 10 vs 0 of 3): the hero's own body, a priceless thing. The remake proof: the same black balls, 8 weeks apart: explained from a boat 8.4M, jumped into the deep end with a countdown 64.6M (7.7x).
7. **Someone reacts** (5 of 10 vs 0 of 3): another person's amazement is proof it was worth watching. For us: a faceless side character jumps back, points, freezes.
8. **End on the peak and pay the promise** (peak 7 of 10 vs 0 of 3; promise 10 vs 1; no advert 10 vs 2). The last second is the "no way" plus the reveal of who it is, never a summary or an ask.
9. **A question alone is not a hook.** "?" titles on the studied channel: 35 Shorts, median 3.4M vs 6.1M without. Our series keeps its question title (owner's rule), so the question must hang on a thing you can picture ("Jumping Into a Pool"), never an abstract idea.

## Numbers table
| Measure | The hits | Our target (the format benchmark wins on format) |
|---|---|---|
| Real object on frame one | 7 of 10 | **1, at 0 s, already moving** |
| Viewer's guess set up | wrong belief 2 + "But" 3 + implied by the picture | **1 line by 3 s, something the viewer has lived** |
| Wait-and-see beat | 8 of 10 | **1, about 1-2 s, a countdown or a hand on it** |
| Spoken tease | 0 of 10 (weak: 2 of 3) | **0** |
| Surprise shown, not said | 6 of 10 | **yes, the "But" is a picture** |
| Voice silent at the reveal | 4 of 10 (4.7-16.7 s) | **the gap at the reveal, 0.5 s max (A/B a longer beat only with the owner's OK)** |
| Body at stake | 5 of 10 | **the hero's own body or prized thing** |
| Someone reacts | 5 of 10 | **1 side character, body language** |
| Length | 58 s | **27-35 s** |
| Cuts | hard, every 3.7 s | **flights (shorts-format rule); hold the reveal shot, don't cut to look busy** |
| Loop | 1 of 10 | **yes (shorts-format rule)** |
| Story blocks | HOOK (object) → short why → TENSION → PAYOFF (shown) → stop | HOOK (object) → GUESS → BUT (shown) → WAIT → REVEAL (no way) → name → LOOP |

## How to apply it in sf-pipeline
**Stage 1 (idea and title):** write the one-sentence idea around a moment the viewer has lived (stepping into water, waiting at the deep end, something falling). The title names that moment, not an idea ("How Did Jumping Into a Pool Get 64 Million Views? 🤯").

**Stage 3 (script):** after the format spine (**shorts-format**) and **sf-story-craft** (villain, bookend):
- Line 1 = a "you" line about the real object on screen, with the obvious guess inside it.
- Replace any spoken tease with a picture of the pending moment.
- Put the "But" on the reveal picture; the voice ends just before it and comments just after.
- The middle explanation is one cause, one picture, short; facts only if they change what the viewer expects.
- Last line: the "no way" and the reveal of who it is, back to frame one.
- The default panel stays **shorts-format-critic + creator-breakdown-critic** (`reference/lessons.md`); run **guess-and-reveal-critic** only when the owner asks.

**Stage 5 (3D, skill sf-blocky-world):**
- Frame one: the hero object alone and big, already moving (foot over the water, finger on the rope).
- The wait: a held shot with one slow push-in and a visible countdown or a hand that hesitates; no flight during the wait.
- The reveal: one shot, no cut, the action on its own real sound (splash, snap, thud); a red arrow or A/B labels if two things are compared.
- A side character reacts in the same shot (jump back, point, freeze).
- Run the survival-story no-voice test (**survival-story-method**): the guess, the wait and the reveal must read with the voice muted.

**Stage 6 (edit, sf-edit):** keep the music low under the reveal and let the real sound lead; check the gap at the reveal is silent of voice and no longer than 0.5 s.

## Self-check before showing the owner
- [ ] A real-looking object about to do something is on screen at 0 s (not a face, chart or map)
- [ ] The viewer's obvious guess is set up by 3 s, about something they have lived
- [ ] A visible wait (countdown, hand, foot) and no spoken tease anywhere
- [ ] The surprise is SEEN; the voice doesn't say it for the picture
- [ ] No voice over the reveal itself; the gap is 0.5 s or less (or an owner-approved A/B)
- [ ] The hero's own body or prized thing is at stake; one side character reacts
- [ ] The last second is the "no way" + the reveal; the title's promise is paid
- [ ] Shorts format kept: 27-35 s, 75-95 words, +16 LU voice over a bed, flights, loop
- [ ] No face, name, footage or screenshot of any real creator; anonymous until the last line
- [ ] Every number is in facts.md with two sources

Source: our own analysis of public videos from Veritasium. Not affiliated with or endorsed by Veritasium.
