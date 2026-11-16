---
name: story-scripts
description: Plan and write a YouTube narration script with a measured story-first method (from our study of a faceless AI-voiced channel, 231k subs, 154k-1M views on all 9 long videos) - common goal, surface and deeper problem, thumbnail first, audience avatars, research gaps, start-to-end transformation, a hero's-journey story under the tutorial, open questions the viewer solves, "but/therefore" links, varied rhythm, and a human-writing pass so the text never sounds AI-written. Use whenever the owner asks to write, fix, outline, roast or humanize a script, voiceover text or story for any YouTube video (long or short), "write the script", "plan the story", "make it sound less like AI", or when a shorts-format skill reaches its script stage.
---

# Story scripts: plan first, story underneath, human on the surface

Learned from the studied creator's "How I Actually Write Viral Scripts" (I07, 287k views) and checked against all 9 of his videos (faceless-channel study of 29 Oct 2026; your own downloads in `<studies_root>/faceless-channel`, shipped notes in `${CLAUDE_PLUGIN_ROOT}/reference/creators/faceless-channel/`; per-video notes in `references/study-data.md`).

**Copy the craft, never the identity:** no ginger suit-and-beard character, no "Steven", no name of the studied creator in our scripts, none of his catchphrases ("let me cook", "secret sauce", "96.2% pure"). Our own channel gets its own running jokes.

**Claude writes, the owner decides.** Show each stage, wait for a yes. This skill is free (no credits).

## The rule over everything
The script is the video. "An amazing edit can't save a boring script or a bad idea." And the studied creator picks **value over retention**: he keeps a useful part even when a retention chart says cut it. Our scripts do the same: never cut a genuinely useful point just to look "optimised", and never end on rage bait.

## Stage 1. Foundation (before one line of script)
Write `plan.md` with:
1. **Idea:** one sentence. Sources: comments, other channels, Reddit, a spark. (Picking ideas: `channel-playbook`.)
2. **Common goal:** what the viewer wants from clicking, and what we want from making it. They must match. If ours is "sell something" and theirs is "learn", the script will feel fake whatever we do.
3. **Surface problem and deeper problem.** The surface is the topic ("how to edit"). The deeper problem is the emotional struggle under it (perfectionism, patience, determination, fear of how you sound). Write both. The deeper problem is never stated at the start; it surfaces in the crisis and is solved at the end.
4. **Thumbnail draft first** (`thumbnail-design`): know the viewer's first impression, because the script has to deliver that promise.
5. **Audience avatars:** 1-3 short profiles (who, how much they know, what they're stuck on). Pick the main one and its complexity ceiling.
6. **Research:** a few hours of videos, articles and AI questions. Note what they explain and, more importantly, **what none of them explain**. That gap is where our video wins.
7. **Start and end point:** where the narrator (or viewer) stands at second 0 and at the last second. There must be a visible transformation ("wants a perfect tutorial" → "learns done beats perfect").

Gate: the owner approves `plan.md`.

## Stage 2. Structure: the story under the content
1. List every point to teach and put them in a logical order, **simple to complex** (context first, then easy ideas, then the advanced ones).
2. Lay the points onto the hero's journey (`references/story-beats.md` has the full map with his editing-video example):
   status quo → call to adventure → mentor → departure → **trials (the actual points)** → approach (the deeper problem shows up) → **crisis** (lowest point, admit weakness) → reward (the lesson) → result → return → new life → resolution.
3. **The mentor:** a second voice who pushes the narrator (his is an inner-voice friend). It costs one extra voice and turns a tutorial into a story. Optional but recommended for long videos.
4. **Universe building (optional, long series only):** each video is a standalone story that also adds a piece to a bigger story across videos (his model: the Marvel films).
5. **Cold open:** never a "hi guys". He opens on a short skit that sets up the call to adventure: a montage of viewer comments asking for the video, a fake-guru hook that gets interrupted, a recording that goes wrong. It names the problem within 30 s, then the title line lands ("So this is how I actually...").
6. **Roast, don't write:** give the outline to an AI and ask "what did I miss, what's boring, what can I cut, is the twist strong?". Never let it write the script; it comes out generic.

Gate: the owner approves the outline.

## Stage 3. Draft fast
Set a timer and type the whole thing from the outline without fixing anything. Expand every point. Add **edit notes in brackets** as you go ("[match cut to the chat window]", "[music drops]"); the editor needs them and the jokes often live there.

## Stage 4. Rewrite with the five tactics from the study
1. **Simple → complex.** Never open with the advanced idea.
2. **Let the viewer figure it out.** Plant a question early ("remember this for the end; see if you can guess it") and pay it off later. Teach like the teacher who gives hints, not the one who reads the lecture.
3. **"But" and "therefore", not "and then".** Rewrite every "and then" join into a turn (but) or a consequence (therefore).
4. **Rhythm.** Mix sentence lengths on purpose. Long winding sentence. Then a short one. A fragment.
5. **Edit notes** stay in the script for the editor.
Then read it aloud: cut boring lines, bad jokes and anything that doesn't serve the goal; add space where a point must land.

## Stage 5. Human-writing pass (do this on every script)
AI-written text is predictable, even and tidy, and both viewers and AI voices make it sound robotic. Read `references/human-writing.md` and fix:
- sentence lengths spread wide (from 1 word to 35+), not all medium;
- fragments, asides, self-corrections ("No, wait."), small talk to the viewer ("Be honest.");
- odd, specific word choices instead of the safe word; concrete details instead of adjectives;
- no neat groups of three, no "So... Then... Finally" chains, no stock phrases or slogans;
- no em dashes in narration text (write a full stop or "..." instead);
- humour that comes from the situation, not from puns.
Run `short-factory\scripts\script_check.py` (sentence spread, repeated openers, stock phrases, "and then" count, triples) and fix every flag.

## Stage 6. Mark up for the voice
Hand the final text to **natural-ai-voice**, which adds the delivery marks (pauses, CAPS stress, "!" and "...", tags) and splits it into 2-4 sentence batches.

## Short-form version (30-60 s shorts, used by shorts-format)
Skip stages 2.2-2.4. Keep: the common goal, one surprising fact as the "gap", simple → complex, one planted question paid off in the last line, but/therefore joins, rhythm, the human-writing pass. The format spine ("you" → wrong belief → "But..." → steps → payoff) already is a but/therefore chain.

## Checks before the script leaves this skill
- [ ] The common goal is written and honest.
- [ ] The deeper problem appears in the crisis and is solved by the end (long videos).
- [ ] The thumbnail promise is delivered, and the title line lands within 30 s.
- [ ] At least one planted question pays off later.
- [ ] No "and then" chains left; sentence-length spread passes `script_check.py`.
- [ ] No stock phrases, no tidy triples, no em dashes.
- [ ] Facts have sources (in `facts.md`).

## Reference files
- `references/story-beats.md`: the hero's-journey map applied to a YouTube video, with his editing and voice videos as worked examples, and the cold-open patterns.
- `references/human-writing.md`: the human-writing rules (the study's 4th voice element plus our GPTZero lessons from the Didit contest form, which reached 99 % human).
- `references/study-data.md`: the measured numbers and per-video notes.
- `short-factory\scripts\script_check.py` (in the plugin's `scripts` folder): `python -I script_check.py <script.txt>`.

Source: our own analysis of public videos from Isaac (@isaacverse). Not affiliated with or endorsed by Isaac or @isaacverse.
