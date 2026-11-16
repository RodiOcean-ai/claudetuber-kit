---
name: game-drama-method
description: Build a short-factory Short (or a title, hook, beat sheet or thumbnail) with the measured game-drama recipe from our study of a chess Shorts channel, turned into faceless 3D - a game moment told as a tiny drama, a feeling or rule-break word in the first line, the subject clear by 1.6 s, a live counter (rating or clock) on the board that rises and falls, one setback and a "But" turn before it lands anyway, board language (yellow last-move squares, a red arrow, a ticking clock), a grey "bad moment" snapping back to colour, a hard stop on the punchline, and short number-promise titles. Use whenever the owner says "game drama", "the chess short", "add a setback", "make something go wrong", "is it a story or a lesson", "Elo counter", "rating counter", "live counter", "chess board scene", "the 3000 Elo trick", or when sf-pipeline writes the script (stage 3) or plans the 3D (stage 5) for an episode about the channel this method was studied from or any episode about a game, a contest or a ranking.
---

# Game-drama method: a game moment told as a drama, with a live counter

Learned from our study of 2 Nov 2026: the studied chess channel's top 10 Shorts (41M-59M), 3 weaker same-format Shorts (0.1M-1.0M), the titles and views of all 1,216 Shorts and 2,257 long videos, and its top 10 long videos. Evidence: `${CLAUDE_PLUGIN_ROOT}/reference/creators/game-drama/SECRET_SAUCE.md`. Numbers: `STUDY.md`, `techniques.md`, story chart `story_blocks.png` in the same folder.

**Copy the craft, never the identity:** no face, name, voice or catchphrases of the studied creator ("Ladies and gentlemen", "Get out of here"), no reaction-cam layout, no real footage of him or of real players. Faceless pieces and toy figures only. Never make claims about real people's behaviour. The creator stays anonymous until the last line (`reference/lessons.md`).

**Claude builds, the owner clicks.** This skill is free: scripts, beat sheets and Blender plans only. Any voice or image generation follows the money rules in `reference/lessons.md`.

**The format benchmark keeps the final word on format.** Where this recipe and the format spine clash, the shorts-format rule wins: 27-35 s, 75-95 words, about 2.8 words/s, voice on frame one, voice about 16 LU above the music, whips not hard cuts, loop to frame one. The studied channel's fast talk (3.5 words/s), close music (10 LU), hard cuts and missing loop did **not** separate its hits from its misses, so we don't take them.

## The recipe (what separated the hits from the misses)
1. **Subject clear by 1.6 s** (7 of 10 hits, 0 of 3 misses). Frame one shows the board, the key piece or the hero object. The proof: "I'm done with this." (44M) vs "I'm done. Bye." (1.0M) have the same opening line, but only the hit shows its subject at 1.6 s.
2. **A feeling or rule-break word in the first line** (8 of 10 hits, 1 of 3 misses): "ruin", "hate", "sorry", "a new rule", "can't do this". It must plant **one specific question** by 3 s (8 of 10 vs 0 of 3): "kings can touch?" is better than "feels illegal to know?". Keep our "you" opening: "If you've ever lost at chess, this will hurt…"
3. **Tell it as a story, not a lesson.** Hits have a **setback in 7 of 10, a "But" turn in 6 of 10 and tension in 6 of 10. The misses have none of them.** The 8-move win (44M) opens as a scene and springs a trap; the 5-move version (0.8M) is just the steps.
4. **A live counter on the board that rises and falls** (3 of 10 hits, 0 of 3 misses). "3000 Elo" (56M, 13 words spoken) is just the rating label falling 2300 → 1200 → 800 → 500 → 200 → 100, then snapping to 3000. Our version: a glowing counter that climbs, drops on the setback, then jumps on the payoff.
5. **Board language:** yellow squares on the last move, one red arrow or ring on the key piece, a chess clock with seconds ticking (tick-tock sound) for tension.
6. **The bad moment goes grey** (2 of 10): drop the colour for the setback, snap back to full colour on the comeback.
7. **Pay off in the last 3-5 s and stop hard** (7 of 10). No ask or plug after the payoff.
8. **Comment question goes in the pinned comment, not in the video.** The studied channel's "Do you agree?" ending has the most comments of its top 10 (14,000). We keep the Short ending on its last word and loop; the question sits in the pinned comment.

## Numbers table
| Measure | The hits | Our target (the format benchmark wins on format) |
|---|---|---|
| Subject readable by | 1.6 s (7 of 10) | **≤ 1.0 s** |
| Feeling / rule-break word | first line (8 of 10) | **first line** |
| Setback beat | 7 of 10 | **1 setback, 40-70 % of the way in** |
| "But" turn | 6 of 10 | **1, before the setback or as the comeback** |
| Counter steps | up to 8 (falling, then a jump) | **4-6 steps: climb, one drop, final jump** |
| New picture every | about 1.5 s | **1.5-2 s** |
| Sound effects a minute | 6 (dings, ticks, bangs) | 4-8: tick-tock on the clock, a thud on the blunder, a ding on the payoff |
| Story blocks | HOOK → LADDER → SETBACK → "BUT" → PAYOFF | the format spine with one SETBACK/COMEBACK inside the ladder |
| Title | 3 words; number titles 2.5M median; "in N moves" 6.0M | question + one emoji, with a number |

## How to apply it in sf-pipeline
**Stage 3 (script):** after the format spine is drafted (**shorts-format**), map it onto this recipe:
- Line 1 = a you-situation with a feeling word, naming the board or piece so the subject is clear at once.
- The escalation ladder = the counter climbing, one step per sentence, numbers written so they caption cleanly (at most 4 spoken numbers; extra steps on screen only).
- One SETBACK sentence ("then one move ruined everything") with the counter dropping, then the "But" comeback.
- Payoff at the biggest number and stop; the last line loops back to the board.
- Run **game-drama-critic** in the expert panel (it advises; shorts-format-critic leads).

**Stage 5 (3D, skill sf-blender-world):**
- Frame one: a chess board at a low three-quarter angle, the key piece big in the centre and a glowing counter card on the board's edge, moving by 0.4 s (push-in).
- Pieces: simple faceless 3D pieces; moves glide and land with a small rocking settle; the last-move squares glow yellow.
- A red ring or arrow on the key piece, on screen ≤ 1.5 s.
- A 3D chess clock with digits that tick down during the tension beat.
- Setback: the counter card drops and shakes, and the world desaturates for 0.5-1 s (keyed in the edit), then colour returns on the comeback.
- Camera beats every 1.5-2 s inside each ≤ 4 s hold; whips between stations; CHECK overlap pass as always; last frame matches the first (loop).

**Thumbnail (sf-thumbnail):** the studied channel's long-video covers pair a shocked face with a cartoon bot and 1-2 big words ("OPENINGS?", "VS"). For us: one glowing king or a counter card as the hero, faceless, 0-3 words of glowing text.

## Self-check before showing the owner
- [ ] Frame one shows the board or the key piece, readable at phone size
- [ ] The first line has a feeling or rule-break word and plants one specific question
- [ ] The counter climbs, drops once on a setback, then jumps on the payoff
- [ ] One "But" turn; the story is a drama, not a list of steps
- [ ] Payoff in the last 3-5 s, nothing after it but the loop
- [ ] Shorts format kept: 27-35 s, 75-95 words, +16 LU voice, whips, loop
- [ ] No face, name, catchphrase or real footage of the creator or of real players; no claims about real people
- [ ] The pinned comment carries the "which creator next?" question

Source: our own analysis of public videos from GothamChess. Not affiliated with or endorsed by GothamChess.
