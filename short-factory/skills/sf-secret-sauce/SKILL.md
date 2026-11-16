---
name: sf-secret-sauce
description: Turn a channel study into "the secret sauce" - the repeatable recipe that makes a creator hit again and again - by comparing the measurements with the shorts-format baseline and every other studied channel, separating format from luck, building an evidence table and a "what we copy / what we don't" list, then LEARNING it as a new SECRET_SAUCE.md, a new method skill and a matching method critic (both named after what the method does, never after the creator) recorded in the tracker; also scores which channel to study next. Use whenever the owner asks "what's their secret", "why do they keep going viral", "what's the recipe", "secret sauce", "what can we copy", "make a skill from this study", "make an expert/critic of them", "which channel next", or right after /study-channel finishes.
---

# Secret sauce: from numbers to a recipe we can reuse

Input: a finished study (skill **sf-channel-study**): the workbook, the study notes, techniques table and story-block chart in `${CLAUDE_PLUGIN_ROOT}/reference/creators/<key>/`.
Output: one recipe the owner can understand in a minute, the evidence behind it, and a new skill and critic so we never have to work it out again.

Plain English to the owner, no paths or code, one question at the end. Be honest: if the "secret" is mostly luck or one record clip, say so.

## 1. Compare (never judge a channel alone)
- **Against the shorts-format baseline** (`reference/creators/shorts-format/STUDY.md`, `skills/shorts-format/references/shorts-data.md`): length, words a second, voice on frame one, pauses, cuts, voice above music, sound effects, captions, loop, title formula, story blocks.
- **Against every other studied channel** (Channels and Patterns sheets in the tracker, each `reference/creators/*/` folder).
- A pattern only counts as theirs if it is **different from the baseline** or **much stronger** in their hits than in their misses.

## 2. Separate format from luck
- Work out each video's **share of total views**. If one clip is a large share (the trick-shot duo's record clip in worked example 1: 39 % of all their Shorts views), set it aside and look at the rest.
- Use **medians per format**, not the best video: a format with one 1.6B hit and a 14M median is a lottery, not a recipe.
- A pattern is a recipe only if it shows up in **most of the hits** (aim for 6 of 8 or better) **and** is weaker or missing in the **misses** (the contrast videos).
- **Remakes are gold:** if the creator remade a winner and it won again, that is proof the format, not luck, did it.
- Check time: is the recipe still working on the newest third of uploads, or decaying?

## 3. Evidence table (goes in SECRET_SAUCE.md)
| # | Pattern | In the hits | In the misses | Proof (numbers) | Confidence |
|---|---|---|---|---|---|
| 1 | ... | 6 of 8 | 1 of 2 | medians, remake pairs | high / medium / low |

Keep 3-6 patterns. Drop anything that is "nice" but not backed by counts.

## 4. What we copy / what we don't
Two short lists:
- **Copy (the craft):** structures, pacing, on-screen devices, title formats, thumbnail layouts that fit a faceless 3D explainer.
- **Don't copy (the identity, or what doesn't fit us):** their name, mascot, faces, catchphrases, voice, real footage; formats that need a live person, a stunt or a location we don't have; anything that is luck.
- One line: **how this would change our next Short** (e.g. "8-10 items, none over 4 s, a counter on screen").

## Worked example 1: a trick-shot duo (31 Oct 2026, the light-study folder)
- Luck vs format: the record clip (5.2B) is **39 %** of their Shorts views; their top 10 are 81 %. So the study looked at the techniques across his hits, not the record.
- Patterns (watched on screen, top 8 hits + 2 contrasts):
  - a **game board on screen in 6 of 8 hits** (numbered list, emoji row, scoreboard): the viewer always knows how many are left and waits for the last one;
  - **everyday objects** a kid owns (bottle, pool, stairs); the 8M flop used an arcade machine and ran 33 s;
  - **8-10 tries per hit, each under 4 s** (the record clip: 8 shots of 2.0-3.6 s; the six biggest run 15-26 s);
  - **remake the winner**: "10 Ways to Flip a Bottle" 806M, remade 16 months later as "10 Coolest Ways" 802M;
  - contrast: **14 basketball Shorts, none over 100M** (median 8.7M): same family, same tricks, no everyday object, no game board.
- What we copied: 10 scenes, none over 4 s; a counter on screen; the bottle as the loop object.

## Worked example 2: the shorts-format story blocks
- The benchmark's blocks: HOOK, WRONG BELIEF, BUT TWIST, ESCALATION LADDER, TEASE, SETBACK/COMEBACK, PAYOFF, LOOP.
- **The escalation ladder replaces conflict in 8 of 10** of the benchmark's top Shorts; a real **setback and comeback in only 3 of 10** (Splinters 217M, Armor 157M, Tootsie 124M); a **payoff in 10 of 10**. Its #1 (Stitches, 255M) has no dip at all.
- Lesson: for a 30 s Short, a climbing ladder of "and then it gets bigger" beats a dramatic low point. Charts: `reference/creators/shorts-format/story_blocks.png`.

## 5. LEARN: make it reusable (free)
Create all three files, in the house style of the existing ones:

1. **`reference/creators/<key>/SECRET_SAUCE.md`**: one-paragraph recipe in plain English, the evidence table, copy / don't copy, "how it changes our next Short", the honest note (luck, decay, what we couldn't measure).
**Name them after the method, never the creator.** Pick one short plain name that says what the recipe does (e.g. `stakes-ladder`, `curiosity-gap`, `verdict`): the skill is `<method>-method`, the critic `<method>-critic`. Never use the creator's name, nickname, handle, channel name or brand in a folder name, `name:`, `description:`, title or trigger phrase, and never write "what would <creator> say" or "<creator>'s recipe".

2. **`skills/<method>-method/SKILL.md`** (style of the method skills, e.g. `stakes-ladder-method`): frontmatter `name` + a pushy `description` with trigger phrases that describe the method; "copy the craft, never the identity" line; "Claude builds, the owner clicks" line; the recipe as a numbered list and a numbers table; how to apply it inside **sf-pipeline** stage 3 (script) and stage 5 (3D); reference files in its own `references/` if long. Under ~180 lines. Inside the text say "the studied channel", never its name.
3. **`agents/<method>-critic.md`** (copy the frontmatter and layout of `agents/shorts-format-critic.md`): a read-only **checklist critic, not a persona**, built **only from our measured study**; it never speaks as or for a real person; it cites `SECRET_SAUCE.md` and the study notes; same 10-point rubric and output (score table, top 5 fixes, factual risks), plus one "Would this fit the <method> recipe?" line. It advises; shorts-format-critic keeps the final say on Shorts format.
4. **One source line at the very bottom** of both the skill and the critic, and nowhere else the channel's name: `Source: our own analysis of public videos from <Channel>. Not affiliated with or endorsed by <Channel>.`

Then record the pairing: the recipe in the tracker's **Secret sauce** sheet; the new skill and critic in **Skills & experts** with `tracker.py add-skill <study_key> "<method>-method" "<what it adds>"` and `tracker.py add-skill <study_key> "<method>-critic" "<what it checks>"`; and one row in the table in `reference/creators/README.md` (study folder, what the method does, skill, critic, channel studied). sf-pipeline finds the episode's method skill and critic there. Add a dated line to the episode's or study's JOURNEY.md.

## 6. Which channel next
Score each candidate in `reference/CHANNELS_TO_STUDY.md` from 0 to 3 on four tests, and keep the list sorted by total:

| Test | 3 points looks like |
|---|---|
| **Helps our Shorts grow** | its craft fits a faceless 3D explainer we can make with our tools |
| **Repeatable formula** | the same format hits again and again (high median, remakes), not one viral clip |
| **Contrast hook** | a number or fact that makes a strong "How did X get Y?" hook (e.g. "89.7M with no words") |
| **Not yet studied** | not in the tracker's Channels sheet (0 if already done) |

Show the owner the top 3 with one line each on why, recommend one, and ask which to study next.

## Tell the owner
3-5 lines: the recipe in one sentence, the strongest proof (one number), what we will copy in the next Short, what we won't, and the question ("Shall I start the next Short with this?").
