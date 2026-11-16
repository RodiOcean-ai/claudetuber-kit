---
name: explainer-styles
description: The base method for making ONE short explainer (same script, same voice, same timing) in many animation styles with Remotion and free local tools, as tested on 14 Nov 2026 with "how to make a peanut-butter sandwich" in 11 styles - the shared beat sheet built from the voice's word times, the free voice recipe (Chatterbox + ClearerVoice, no time-stretching), the music bed and sound-effect copies, a review page with one tab per style where the owner pins notes and approves each style, the graphics-card traffic light, cut-outs from the local picture maker, the render with the -12 LUFS master and subtitles, and the per-style work log with exact numbers. Use whenever the owner says "make it in N styles", "the 11 styles", "explainer styles", "same video in another style", "style test", "review page with tabs", "render the approved styles", "which style is hardest", or before using any explainer-<style> skill (kinetic typography, motion graphics, screencast, isometric, whiteboard, comic, 2.5D, collage, 2D character, 3D animation, stop motion).
---

# One explainer, many styles (the base method)

Plain English to the owner: "the review page", "the voice", "the beats", "the picture maker", "rendering". No paths or code in
replies, one question at the end. The style skills (`explainer-<style>`) hold the look of each style; this skill holds what
every style shares. The reference build is in `reference/` (shared code, review page, tools) and each style skill's
`reference/` holds its component.

## The order of work (owner's rules)
1. Ask once: frame shape (16:9 for a long video, 9:16 for Shorts) and the shared script (about 35-40 words, 4-5 steps,
   15 s; a small joke as the last line gives every style a payoff). Same script, voice and timing in every style, so the
   comparison is fair.
2. Voice (free, local) -> word times -> the beat sheet (frames) that every style reads.
3. Build styles easiest first; show each on the review page as soon as it is ready (do not wait for all of them).
4. The owner pins notes on the page; fix, reply under each note, raise the build label ("Build 2").
5. Render ONLY the styles approved on the page, re-render only what changed.
6. After approval, write or update the style's skill from what really happened.

## The voice (free, local; the owner's pick of 14 Nov 2026)
- **Chatterbox, cloned from the channel's voice sample** (`reference/tools/make_voice3.py`): 8 takes = 2 punctuation
  versions x 2 settings x 2 seeds. Same words as the script; punctuation only shapes the pauses ("bread... then dig").
  Settings that read calm: exaggeration 0.4, cfg 0.3 (about 3.2 words a second).
- Pick a take that is word-perfect (Whisper check, `reference/tools/words.py`) AND has a silent gap at every step boundary.
- **ClearerVoice MossFormer2_SR_48K** rebuilds the missing highs (`reference/tools/clearvoice_sr.py`). Run it on the
  PROCESSOR (traffic light `-CpuOnly`): on a busy graphics card it froze for over an hour; on the processor it is slow but safe.
- **Never time-stretch.** The first build slowed Chatterbox's built-in voice to 0.94 with rubberband and the owner heard it
  at once: "shaky and robotic". Fill the 15 s with longer pauses only at sentence breaks instead.
- Place each phrase at its planned start by cutting only inside the take's own silent gaps, found by SOUND LEVEL, never by
  Whisper's word times (`reference/tools/assemble_voice.py --tempo 1 --sr 48000 --starts ...`). One fixed gain after; no
  compressor, no loudness-normalising of the voice.
- Whisper's first word of every phrase starts too early (it swallows the silence before it). `reference/tools/timing.py`
  starts each phrase's first word at the phrase's measured start and keeps Whisper's times inside the phrase.

## The beat sheet (`reference/shared/timing.ts`)
`WORDS` (frame of every word), `K` (names for the word numbers the pictures act on), `at(k)`, and `STEPS` (which frames
belong to each step). Every style animates from these; a word's picture lands 2 frames BEFORE the word is heard. When the
voice changes, rebuild `words.json` / `phrases.json` and every style follows without edits (the 14 Nov voice swap moved
every step by under 0.2 s and needed no style changes).

## Music and sound effects
- House music first (the owner's paid library). For 15 s, take the LAST 15 s of a cue that ends naturally, so the music
  resolves at the end; set it once about 15 LU under the voice and lift it about 5 dB after the last word.
- Copy sound effects with `reference/tools/sfx.py` (lead silence trimmed, peak -6 dBFS) and give every on-screen action its
  own sound (land, pop, swish on camera moves, a thud on PRESS, a whip on the cut).

## The review page (one tab per style)
`reference/review/serve.py` + `ReviewApp.tsx` + `index.html`: plays every style LIVE with the Remotion Player (nothing is
rendered), one tab per style with a dot for open notes and a green number when approved; the owner clicks a spot, types a
note, reads Claude's reply, approves each style. `serve.py notes`, `reply <style> <n> "text" done`, `build <style> "Build N"
--change ...`. Add a launch config so it opens in the app's browser pane.
- Newer version (the sandwich project uses it): the `review-page` skill and `templates/review-page/` add an
  editor-style timeline (voice with every word, music, sound effects), whole-video comments (C) and notes on one sound.
- `?clean` shows only the video, filling the window: use it for Claude's own frame checks (seek with
  `window.reviewPlayer.seekTo(n)` and take a screenshot).
- 3D styles sometimes draw a blank frame after a seek in the browser pane while the graphics card is busy: seek to the
  next frame and back. They play and render fine.

## The graphics-card traffic light (owner's rule, 14 Nov 2026)
One graphics card, one job at a time. The owner runs every picture batch and every render through a small turn-taking
script of his own (a "traffic light", not included in this kit: it waits until the card is free, then runs the command;
one turn for a whole batch); speech recognition and voice clean-up run on the processor. Without such a script, simply
never start two card jobs at once. If you do use such a script, give it a small `.cmd` file
(bash and `py` scripts with spaces in their paths did not start), and check its output: a job that "finished" may have run
nothing.

## Pictures (free local picture maker)
- One prompt list per style; 3-4 tries per picture; look at every one (contact sheets: `reference/tools/contact.py`).
- "Pure green background" comes out dull green with a light patch, so a plain green key cuts the light patch as part of the
  object. Use `reference/tools/grab_cut.py` (GrabCut, then drop green-tinted shadow pixels; `--metal` for knives);
  white-background items by colour saturation; hands by skin + steel colours.
- The default negative prompt of the picture script forbids "cartoon, illustration": pass your own for drawn styles.
- The model will not draw a sandwich cut corner to corner from above: generate the WHOLE sandwich from straight above and
  cut it into two triangles in code (clip paths), with the peanut-butter line drawn along the cut.

## Render and master (`reference/tools/render.py`)
Refuses any style without an approval for its current build. Renders with the Remotion CLI (`--gl=angle`, concurrency 6,
CRF 16), then the house master: two-pass loudnorm to -12 LUFS, true peak -1 dB, linear. With the free voice's peaks the
linear pass stops near -13.2 LUFS (the true-peak ceiling); that is accepted (no limiter: one fixed voice volume).
`reference/tools/srt.py` writes the subtitle file once (all styles share the voice) and copies it next to every MP4.

## The log (exact numbers win in this niche)
`log/LOG.md`: one line when a style starts, when its first build is ready (with the self-check fixes), every owner note
round, approvals, and each render's seconds. Pictures in their own log (generations made / kept, minutes).

## Measured on 14 Nov 2026 (peanut-butter sandwich, 15 s, 1920x1080)
| Style | Build (min) | Owner notes | Fix rounds | Render (s) |
|---|---|---|---|---|
| Kinetic typography | 7 | 0 | 0 | 38.4 |
| Motion graphics | 4 | 0 | 0 | 16.9 |
| Screencast | 4 | 0 | 0 | 19.4 |
| Isometric | 5 | 2 | 1 | 16.4 |
| Whiteboard | 3 + 21 pictures | 0 | 0 | 18.0 |
| Comic | 15 + 7 pictures | 1 | 1 | 25.9 |
| 3D animation | 6 | 1 | 1 | 19.7 |
| Stop motion | 3 | 2 | 1 | 19.0 |
| 2D character | 8 | 2 | 2 | 13.0 |
| 2.5D | 21 together with collage + pictures (33 tries, 11 kept) | 4 | 1 (22 min with collage: rebuilt as a top view, 27 tries) | 22.8 |
| Collage | (same 21) | 3 | 1 (same 22 min, 9 tries) | 21.7 |
All 11 renders: 231 s in total (13-38 s each), every one checked by eye (4 frames) and measured (about -12.6 LUFS).
Shared setup (voice, music, project, review page): 19 min. Voice remake on the owner's note: 8 takes (8 min) +
ClearerVoice on the processor (75 min, because the graphics card was frozen by two jobs at once).

## Pitfalls (all happened on 14 Nov)
- A spring that overshoots makes a falling slice sink INTO the board for a frame ("the bread disappears"): clamp the
  height at the landing and turn the overshoot into a squash.
- Props standing inside other props (a jar half inside the board): place everything on the board's top, or behind it.
- An open jar must look open: a rim, not a solid lid disc.
- A character holding a knife: the hand holds the HANDLE; the blade must be the part that touches the bread. Check the
  spread frames for which end touches the food.
- Shapes for the cut must be real closed solids (clip the outline polygon, extrude each half), or the halves look hollow.
- Never run a second graphics-card job while another one runs: two at once froze the card for over an hour.
- Photo cut-outs seen at an angle never line up with the table or with each other, and the picture maker will not draw a
  corner-to-corner cut: make the pictures TOP-DOWN and do the cut in code (clip the whole-sandwich picture into two
  triangles through its measured corners). This fixed 2.5D, collage and comic.
