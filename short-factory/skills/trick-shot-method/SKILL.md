---
name: trick-shot-method
description: Build a short-factory Short (or its idea, hook, beat sheet, 3D plan or cover word) with the measured trick-shot recipe from our study of a top trick-shot Shorts channel, turned into a 30-second faceless 3D Short in our underwater lab - one figure, one target the viewer can see and one deciding moment big in the middle of the frame so the viewer bets on every try from second one, the bet said in line one, a ladder that climbs easy -> hard -> "impossible", a friend who fails and gives up at 18-22 s, a faceless specialist who lands it after a visible pile of misses at 80-90 % of the Short, the impact sound in the clear, a real sound for every try, and "IMPOSSIBLE" as the cover word. Use whenever the owner says "trick shot", "trick-shot check", "the impossible wall", "easy hard impossible", "bring in the pro", "bring in the big guns", "the bet", "will it go in", "can the viewer see the target", "miss counter", "34 tries", "the miss makes the make", or when sf-pipeline writes the hook or script (stage 3) or plans the 3D (stage 5) for an episode about the channel this method was studied from or any episode built around one try at one target.
---

# Trick-shot method: one target you can see, a bet on every try, the miss that makes the make

Learned from our study of 15 Nov 2026: the studied channel's top 10 Shorts (94M-281M), 3 weak Shorts (0.28M-0.57M), the titles of all 242 Shorts and the top 10 long videos. Evidence: `${CLAUDE_PLUGIN_ROOT}/reference/creators/trick-shot/SECRET_SAUCE.md`. Numbers: `STUDY.md`, `techniques.md`, story chart `story_blocks.png` in the same folder.

**Copy the craft, never the identity:** no face, name, logo, arena, footage, song or catchphrase of the studied creators, and no star, trophy or name card of a real person. Faceless blocky figures only; the creators stay anonymous until the last line (`reference/lessons.md`).

**Claude builds, the owner clicks.** This skill is free: ideas, scripts, beat sheets and Blender plans. Voice and image generation follow the money rules in `reference/lessons.md`.

**The format benchmark keeps the final word on format.** The studied channel's 40 s, 34 words, 1.4 words/s, voice only 3 LU above the room, no captions and no loop do not apply. The shorts-format rule wins: 27-35 s, 75-95 words, about 2.8 words/s, voice on frame one, voice about 16 LU above the music, captions, loop to frame one.

## The recipe
1. **One figure, one target you can see, one deciding moment in the middle of the frame** (10 of 10 hits, 0 of 3 weak). The viewer must be able to bet "will it go in?" in the first second. The target never leaves the frame and never moves in it; the outcome happens on screen, not off it. Weak Shorts lost this: a home run leaving the frame, a cluttered drone view, a pile of bodies hiding the ball.
2. **Something already moving at 0 s** (10 of 10 vs 1 of 3): the throw in the air, the ball rolling toward the cups, the hammer raised.
3. **Say the bet in line one** ("easy, hard, and impossible", "level 1 to 12" in 4 of 10; the written question in a 5th). For us: the stake in the first sentence, with the subject in the first three words.
4. **Climb, don't repeat** (ladder to "impossible" in 5 of 10 vs 0 of 3; all 3 weak repeat one try). Three rungs, each harder; the hardest last.
5. **The miss makes the make** (3 of 10, all three impossible-wall Shorts: 127M, 281M, 99M, made in seven weeks). A friend misses the top rung and gives up; a specialist walks in; the counter climbs past 20 (34, 30, 21 tries); the make lands at 77-92 % of the way through.
6. **The picture tells it, the sound proves it:** the hits' words median 34 vs 104 in the weak; 17.7 action sounds a minute vs 2.1. For us: every try gets its own real-sounding hit, the make's impact plays in the clear (the silent beat before the punchline, 0.5 s at most), and each sentence names what the picture already shows.
7. **Close the bet before patience runs out:** all 10 hits at 58 s or less. Ours: 27-35 s (shorts-format rule).
8. **Cover word "IMPOSSIBLE"** ("impossible" titles: 13 Shorts, median 11M, about 2x the channel in both eras), in our yellow style, the target and the figure visible behind it.

Not the secret (both hits and weak have it): a try counter on screen, fast cutting, a bright first frame, music. A counter is fine as a picture, never as the reason.

## Numbers table
| Measure | The hits | Our target (the format benchmark wins on format) |
|---|---|---|
| Target visible and centred | 10 of 10 | **from frame one, centre third, never leaves** |
| Moving at 0 s | 10 of 10 | **the throw already in the air at 0 s** |
| Ladder rungs | 5 of 10 climb to "impossible" | **3 rungs, hardest last** |
| Friend fails, specialist lands it | 3 of 10 (the biggest wall Shorts) | **give-up at 18-22 s, make at 24-27 s** |
| Tries shown before the make | 21-34 on the counter | **a counter that runs past 20** |
| Action sounds a minute | 17.7 (weak 2.1) | **one per try, never two within ~8 frames** |
| Words | 34 (weak 104) | **75-95, each naming what is on screen** |
| Voice above background | 3 LU | **14-18 LU above the music bed (shorts-format rule)** |
| Length | 40 s (all 58 s or less) | **27-35 s** |
| Loop | 0 of 10 | **yes (our rule)** |
| Story blocks | HOOK → LADDER → TENSION → SETBACK → COMEBACK → PAYOFF | HOOK → BELIEF → BUT → LADDER → SETBACK → COMEBACK → PAYOFF/REVEAL → LOOP |

## How to apply it in sf-pipeline
**Stage 1 (idea and title):** the one-sentence idea must touch something the viewer has lived (throwing paper at a bin, a last-second shot) and contain one target and one try. Check earlier episode titles first: the water bottle and "you never see a miss" belong to our first episode (a trick-shot duo).

**Stage 3 (script):** after the format spine (**shorts-format**) and **sf-story-craft**:
- Line one says the bet while the throw is already in the air.
- Wrong belief: "a great trick shot is all about the make". The "But" at 5-9 s turns the misses into the story (the counter climbing, the friend about to quit), without claiming the counter itself wins views (it doesn't separate hits from weak).
- Ladder of three rungs joined with "so… but…" (the creator-breakdown chain when **creator-breakdown-method** is used); the friend's give-up is the setback at 18-22 s.
- The specialist's make lands at 80-90 %; the reveal names the creators in the last line and returns to the target.
- Run **trick-shot-critic** only if the owner asks; the panel is shorts-format-critic (lead) + creator-breakdown-critic.

**Stage 5 (3D, skill sf-blocky-world):**
- Frame one: one blocky figure, the target (a slot, a hole, a bin) dead centre and readable at phone size, the object already flying. Eye-level framing, the camera moving slowly around a target that stays put.
- Rungs = the same target wall with three holes, easy to impossible (green ring on each made hole).
- The give-up: the friend drops the stick or falls (Ginger's 1.6 s splat can carry this beat). The specialist: a faceless figure with a plain "THE PRO" card, no real name.
- The make: centred, big, a short slow push-in; the impact sound in the clear; a green ring or flash on the hole.
- The series Easter egg (the bottle) stays out of the target's line of sight.

**Thumbnail (sf-thumbnail):** the figure mid-throw, the tiny target centred with one red circle or arrow, 0-3 glowing words ("IMPOSSIBLE" or the try number), the creators unnamed.

## Self-check before showing the owner
- [ ] A stranger can bet "will it go in?" by 1 s: one figure, one target, both readable at phone size
- [ ] The target stays in the frame and the outcome happens on screen, centred
- [ ] Something is already moving at 0 s
- [ ] Three rungs that climb; no rung repeats the one before
- [ ] A give-up at 18-22 s and a make at 24-27 s, the impact in the clear
- [ ] A real-sounding hit for every try; no stacked sounds
- [ ] Shorts format kept: 27-35 s, 75-95 words, voice 14-18 LU above the bed, captions, loop
- [ ] No face, name, logo, trophy, star or footage of any real person; anonymous until the last line
- [ ] Every number in facts.md with two sources; the try count read from the on-screen counter

Source: our own analysis of public videos from Dude Perfect. Not affiliated with or endorsed by Dude Perfect.
