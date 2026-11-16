---
name: stakes-ladder-method
description: Build a short-factory Short (or a title, hook, beat sheet or thumbnail) with the measured stakes-ladder recipe from our study of a top Shorts channel, turned into faceless 3D - a hero object filling frame one, the stake said in the first breath, a glowing number tag that climbs 4-6 steps, one "will it land?" try, payoff at the highest point plus a dry sting, a new picture every 1.5-2 s, red arrows on the one detail that matters, and "X vs Y" / "How many X to Y?" title formats. Use whenever the owner says "stakes ladder", "stakes check", "add a ladder", "climbing price tag", "$1 vs $X", "raise the stakes", "make the hook pop", "the stake feels flat", or when sf-pipeline writes the script (stage 3) or plans the 3D (stage 5) for an episode about the channel this method was studied from or any episode that needs a stronger stake.
---

# Stakes-ladder method: a stake you can see, climbing, then one try

Learned from our study of 31 Oct 2026: the studied channel's top 10 Shorts (1.0B-1.9B), 3 weaker same-format Shorts (66M-95M), the titles and views of all 205 Shorts and its top 10 long videos. Evidence: `${CLAUDE_PLUGIN_ROOT}/reference/creators/stakes-ladder/SECRET_SAUCE.md`. Numbers: `STUDY.md`, `techniques.md`, story chart `story_blocks.png` in the same folder.

**Copy the craft, never the identity:** no face, name, voice, catchphrases, real footage, thumbnails or logo of the studied creator. No money giveaways, "subscribe to win", sponsor reads or real people. Silhouettes and faceless toys only. The creator stays anonymous until the last line (`reference/lessons.md`).

**Claude builds, the owner clicks.** This skill is free: scripts, beat sheets and Blender plans only. Any voice or image generation follows the money rules in `reference/lessons.md`.

**The format benchmark keeps the final word on format.** Where this recipe and the format spine clash, the shorts-format rule wins: 27-35 s, 75-95 words, about 2.8 words/s, voice on frame one, voice about 16 LU above the music, whips not hard cuts, loop to frame one. The studied channel's own loud music, 39 s length and missing loop did **not** separate its hits from its misses, so we don't take them.

## The recipe (what separated the hits from the misses)
1. **Hero object big and readable by 1.2 s, moving by 0.4 s** (8 of 10 hits, 1 of 3 misses). One thing everyone understands, filling the frame. No wide establishing shot.
2. **Stake in the first breath:** a yes/no "Can you…?" / "Would you…?" or "If you…" line (best measured hook, 8.8/10: "Can you slice a bullet with a katana?"). This also passes our "open on a you-situation, never a statistic" rule.
3. **Optional flash-forward:** show the payoff frame for about 0.5 s around 0.8 s, then go back and build to it.
4. **A glowing number tag that climbs 4-6 steps** (6 of 10 hits, 0 of 3 misses): price, views, size, speed. Each step is clearly bigger. The model is "Car Doors": $100K → $1M → $2M → $10M → $50M → $100M. **Never let the steps shrink**: the 69M miss ran its prizes downhill.
5. **One "will it land?" try** carries the middle (9 of 10 hits). A miss or near-miss is allowed (4 of 10), but something must keep rising.
6. **Payoff at the highest point, then one dry sting line, then stop** (payoff highest in 10 of 10; sting in 5 of 10). Measured stings: "before they figured out the whole door thing", "I honestly just needed one". No call to action before the payoff.
7. **Pictures every 1.5-2 s** (the hits: median shot about 1.1 s, 40 cuts a minute; misses 2.1-14 s). Within our ≤4 s scenes, add push-ins, whips and cutaways so the eye gets something new about every 2 s. **But speed is not the trick:** a former lead editor of the studied channel says hyper-fast cutting now loses viewers when it hides a weak story. Each new picture must show the words; never cut just to hit the count. Copy the structure (stake, ladder, payoff), not the production look.
8. **On-screen devices:** a glowing number tag that pops on with a small sound; a **red arrow or circle** on the one detail; captions of 1-3 words, white with a black outline, low centre.

## Numbers table
| Measure | The hits | Our target (the format benchmark wins on format) |
|---|---|---|
| Hero object readable by | 1.2 s (8 of 10) | **≤ 1.0 s** |
| Stake said by | ≤ 3.3 s (8 of 10) | **≤ 3 s** (the first line) |
| Ladder steps | 3-6 (6 of 10) | **4-6, always rising** |
| New picture every | about 1.1 s | **1.5-2 s** |
| Sound effects a minute | about 9 | 4-8 soft pops and whooshes, on the tags and whips |
| Story blocks | HOOK → LADDER → TENSION → PAYOFF (+ sting) | the format spine with the LADDER as the escalation and one TENSION beat |
| Title | "X vs Y" 553M median, "How many X to Y?" 552M | question + one emoji in that shape |

## How to apply it in sf-pipeline
**Stage 3 (script):** after the format spine is drafted (**shorts-format**), map it on to this recipe:
- Line 1 = the you-question naming the hero object and the stake.
- The escalation ladder = the number tag climbing, one tag per sentence, each written as a whole number so it captions cleanly. Use 4-6 steps; all numbers count towards our maximum of 4 *spoken* numbers, so put extra steps on screen only.
- One sentence of "will it…?" tension before the payoff.
- Payoff at the top number, plus a dry sting of 4-8 words, then the loop line back to the hero object.
- Run **stakes-ladder-critic** in the expert panel (it advises; shorts-format-critic leads).

**Stage 5 (3D, skill sf-blender-world):**
- Frame one: the hero object fills about 60 % of the vertical frame, moving at 0.4 s (push-in or rotation).
- A tag object (glowing green or gold text card) parented to the hero; it scales up on each step, with a pop sound in the edit.
- One red arrow or ring model for the detail that matters, on screen ≤ 1.5 s.
- Camera beats every 1.5-2 s inside each ≤4 s hold (push-in, orbit step, whip). Run the CHECK overlap pass as always.
- Last frame matches the first (loop), so the sting must be said over the hero object.

**Thumbnail (sf-thumbnail):** the studied channel's "$1 vs" covers are a split screen, cheap and broken on the left, gold and shiny on the right, with two short numbers in the corners. For us: the anonymous hero object in both states, 0-3 words of glowing text.

## Self-check before showing the owner
- [ ] Frame one is the hero object, readable at phone size, moving by 0.4 s
- [ ] The first line asks a you-question with the stake in it
- [ ] 4-6 tag steps, every one bigger than the last
- [ ] One "will it…?" beat, then the payoff at the highest number
- [ ] Sting of 4-8 words, no "subscribe" and no sponsor before it
- [ ] A new picture at least every 2 s; no scene over 4 s
- [ ] Shorts format kept: 27-35 s, 75-95 words, loop, +16 LU voice
- [ ] No face, name or real footage of the creator; reveal in the last line only

Source: our own analysis of public videos from MrBeast. Not affiliated with or endorsed by MrBeast.
