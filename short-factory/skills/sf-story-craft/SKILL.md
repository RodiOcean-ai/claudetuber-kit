---
name: sf-story-craft
description: The storytelling pass for a short-factory script - every line must have a job (Chekhov's gun), a villain (the "mega mean mouse": stack consequences, blame outside forces, dead solutions, why they failed), the story structure picked by the feeling we want (Save the Cat for satisfaction, Problem-Agitation-Solution for momentum, Hero's Journey for transformation, And-But-Therefore for clarity) and mapped onto the format spine, an unpredictable first line, an establishing shot, word pictures we can show, facts sugar-coated in drama, and a bookend ending that returns to the opening with a twist instead of a predictable loop. Learned from a public talk on the psychology of storytelling (2026). Use whenever the owner says "storytelling", "every line needs a purpose", "villain", "bookending", "Save the Cat", "problem agitation solution", "hero's journey", "and but therefore", "the story is flat", "the ending is predictable", "line by line", or at sf-pipeline stage 3 before the expert panel.
---

# Story craft: every line earns its place

From a public talk on the psychology of storytelling (467k views, Jan 2026; see the source line at the bottom). Full notes: `${CLAUDE_PLUGIN_ROOT}/reference/methods/storytelling-talk-notes.md`. **The shorts-format study's measured rules still decide the format** (75-95 words, "But" at 5-9 s, loop, captions); this skill decides whether each line pulls its weight. The owner's own wording wins; changes to it are proposals. Free, no credits.

## When it runs
Stage 3 of **sf-pipeline**: after the first draft passes `script_check.py`, **before** the expert panel. Write the result as `story_craft.md` in the episode and log one line in JOURNEY.md.

## 1. Pick the structure by the feeling (one sentence first: "the viewer should end up feeling ___")
| Feeling we want | Structure | How it sits on the format spine (hook -> wrong belief -> But -> ladder -> payoff -> loop) |
|---|---|---|
| **Clarity** ("oh, that's how it works") | **And-But-Therefore** | hook + belief = AND, the twist = BUT, the ladder = THEREFORE. Our default. |
| **Momentum / urgency** | **Problem-Agitation-Solution** | hook = problem, belief + the setback = agitation (make it worse), the ladder + payoff = solution. |
| **Transformation** (nobody -> giant) | **Hero's Journey**, compressed | ordinary world (frame one) -> call (the hook) -> trials (ladder) -> lowest point (setback) -> return changed (payoff + bookend). |
| **Satisfying rhythm** (long videos) | **Save the Cat** | opening image, theme stated, catalyst, midpoint, all is lost, finale. Too many beats for 30 s; use it in `what-if-longs`. |
Choosing the wrong one makes the brain feel a clash; say which one and why in `story_craft.md`.

## 2. The villain (a "mega mean mouse", never a real person)
What is stopping the viewer, or stopped the creator? Make it specific and visible. In four short moves (one clause each in a Short):
1. **Stack the consequences** ("hours-long games", "nobody watches").
2. **Blame outside forces** (the algorithm, the format, the gatekeepers).
3. **Dead solutions** (what everyone else tried: "be the best player", "buy a studio").
4. **Why they failed** (one line).
Our villains are obstacles, beliefs or the swipe itself (boredom, "you need a title", "you need a face"). Never a named creator, player or company. In the 3D world the villain gets a picture (the giant grey hourglass, the shadow).

## 3. Line-job table (Chekhov's gun)
For **every** line, write its job. Allowed jobs: **hook** (plant the question), **orient** (where/who/vibe/focus), **wrong belief**, **villain**, **twist (But)**, **proof** (a number, a fact), **ladder step** (bigger than the last), **setback**, **payoff**, **bookend**.
| # | Line | Job | Picture it shows | Planted / paid off |
|---|---|---|---|---|
- A line with no job is cut. Two lines with the same job: merge or cut one.
- **Every planted thing is paid off** (a question, an object, a number, a word): the last column must have no loose ends. Every emphasised object in the 3D world counts too: if the camera lingers on it, it must come back.

## 4. Line-level tests
- **First line (predictive processing):** read it alone. Do we know what it's about? Are we intrigued? Can we *not* guess the answer? All three yes. A sensory or specific anchor beats a slogan.
- **Establishing shot:** the first line plus frame one answer *where, who, what vibe, what to look at* (matches "subject clear by 1.6 s").
- **Word pictures:** close your eyes while the text-to-speech reads it. Every line must make a picture we can show; swap summary words ("success", "strategy", "content") for things (a crown, two phones a day, a flying rook). Add colour, texture or shine where it helps.
- **Sugar coating:** each fact rides on drama, conflict, humour or motion. No fact is read out as a list.

## 5. Bookend with a twist (not a predictable loop)
The loop returns to frame one, but **the meaning has changed**:
- Plant something in the opening worth returning to: an image that can transform, a question that gets a *different* answer than expected, or a belief that gets reversed.
- The ending is the one the viewer wants, but not the expected way (Shrek: Fiona becomes the ogre).
- **Test:** remove the bookend. If the story still feels complete, the ending is decoration; rewrite it.
- The picture loop (last frame = first frame) stays a format rule; the twist lives in the words and in one changed detail on the board.

## Output: `story_craft.md`
1. Feeling + structure chosen, one line why.
2. The villain in four moves (or why this story has none and what replaces it).
3. The line-job table.
4. The four line-level tests: pass / fail with the line.
5. The bookend: what is planted, how it returns, the twist.
6. Proposed changes as a numbered list (the owner's wording marked "proposal only"), then `script_check.py` again.

## Tell the owner
Two to four lines: the structure and villain in plain words, the 1-3 lines that have no job or no picture, the bookend twist, then one question ("Shall I apply these changes?").

Source: our own notes on a public talk by Joanna Wiebe ("The Psychology of Storytelling That Will Change Your Life"). Not affiliated with or endorsed by Joanna Wiebe.
