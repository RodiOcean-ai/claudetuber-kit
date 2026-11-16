---
name: sf-expert-panel
description: The critic loop for a short-factory script, title, hook or finished Short - shorts-format-critic leads and has the final say on Shorts format, story-critic, hook-oracle and the episode's method critic advise; a fresh panel each round, at most 5 rounds, stop on a plateau, keep only fixes two or more critics agree on, the owner's own wording always wins, scores reported honestly; plus the short critic-chat format. Use whenever the owner says "critique this", "score the script", "run the critics", "/critic", "format check on the script", "format critic vs story critic", "roast the script", "get it to 9", "expert panel", or when sf-pipeline reaches the script stage.
---

# Expert panel: critics advise, the format critic decides format, the owner decides

What we learned the hard way (our first episode, about a trick-shot duo: two loops of 5 rounds each: 5.6 -> 6.7 and 6.5 -> 6.6): **critic loops plateau around 6.5-7.** Fresh critics find new problems each round and contradict each other, so scores go sideways. The panel exists to catch real mistakes (wrong facts, a hook that opens on a statistic, a reveal nobody asked for), not to chase a number.

Plain English to the owner, no paths or code, one question at the end.

## The panel
| Critic (agent) | Role | Final say on |
|---|---|---|
| **shorts-format-critic** | lead | Shorts format: spine, length, words a second, hook shape, captions, loop, title formula |
| **story-critic** | advises | planted question and payoff, story under the facts, human writing, the reveal ending |
| **hook-oracle** | advises | the first 3 seconds (8 tests, its own score out of 10) |
| **the episode's method critic** (if any) | advises | does it use the subject's secret sauce correctly: the critic paired with the subject's study in the table in `reference/creators/README.md` or in the tracker's Skills & experts sheet (e.g. stakes-ladder-critic) |
| **fact-checker** | not a scorer | every claim has two sources; reports, never edits |
| **The owner** | decides | everything; his own wording beats any critic's rewrite |

All critics are checklists built **only from our measured studies**, named after the method they check. They are not personas: they never speak as or for any real creator and never claim to.

## How to run one round
1. **Brief each critic the same way:** the script text (with word count and read time at 2.8 words/s), the title, the beat sheet or scene plan, the thumbnail idea, `facts.md`, the series rules from `reference/lessons.md`, and the episode's `story_craft.md` line-job table if there is one (skill **sf-story-craft**). **Never include our own opinion** of the script, or they will just agree with it.
2. **Fresh critics every round:** start new agents each time (no memory of earlier rounds), and run them **in parallel** in one message.
3. Each returns the shared score table (rubric below), top 5 fixes and factual risks. hook-oracle returns its 8-test table; use its total / 5 as the "hook" line if needed.
4. **Merge:** keep only fixes **two or more critics** agree on, plus any factual error (one is enough for facts). On a format clash, **shorts-format-critic's rule wins**. A fix that rewrites the owner's own wording is a *proposal* for the owner, never applied silently.
5. Apply the kept fixes, run `script_check.py` again, write the round in the script file and JOURNEY.md.
6. **Owner notes that are a feeling, not a fix** ("not there yet", "doesn't feel right", "boring in the middle"): turn them into a numbered list of 3-6 concrete changes (what, where, why), show it, and change nothing until the owner OKs it. A top channel's editors needed a year to decode vibe notes; a written list skips that.
7. **A "cut faster" fix is not automatic:** when a critic asks for more pictures or cuts, the new picture must show the words being said. More cuts cannot rescue a weak story (lesson from a former lead editor of a top channel); fix the story first.

## The shared rubric (10 points)
| Part | Points | Full marks looks like |
|---|---|---|
| Hook | 2.0 | "you" situation, subject in the first 3 words, voice and motion on frame one, no statistic first |
| Planted question | 1.5 | one specific question early that the last line pays off |
| Depth | 1.5 | explains *why* it works (a mechanism), not just *that* it worked |
| Accuracy | 1.5 | every claim matches facts.md with two sources; no "if" sentence that claims something about the viewer |
| Format recipe fit | 1.5 | 75-95 words, "But" at 5-9 s, escalation ladder, payoff, loop, 0-4 numbers, 1-3-word caption phrases |
| Rhythm | 1.0 | mixed sentence lengths, no tongue-twisters, speakable at 2.8 words/s, scenes of 4 s or less possible |
| Ending | 1.0 | the reveal lands last, loops back to the opening, no outro or "subscribe" |

## Stop rules
- **Maximum 5 rounds.** Never more, even if the owner asked for "until 9.5" (tell him why).
- **Stop on a plateau:** if the average moves less than 0.3 for two rounds in a row, stop.
- Stop at once when the owner says the script is right. **His ear decides.**
- After the last round, apply the agreed fixes and mark the version "final, unscored" if it was not scored again.

## Report honestly
- Show the round table: round, version, average score, each critic's score, biggest fix made.
- Never round up, never hide a low score, never call 6.6 "nearly 7 so basically there".
- Say plainly when critics contradicted each other and what was decided.

| Round | Version | Format | Story | Hook | Avg | Biggest fix |
|---|---|---|---|---|---|---|
| 1 | v2 | 6.0 | 5.5 | 5.8 | 5.8 | hook opened on a statistic |

## The critic chat (when the owner asks "what do the critics say" or two critics disagree)
Short alternating turns, each citing a rule or a measured number from our studies. Then the settlement. Example (first episode, v15):

> **shorts-format-critic:** "Five point two billion" sits mid-sentence. Anchor it: "the most-watched Short ever". (Rule: one scale surprise, said simply.)
> **story-critic:** Agree. But keep "It lands. Reward." Fragments give the ear a beat. (Rule: vary sentence length.)
> **shorts-format-critic:** Fine, if each still splits into 1-3-word captions. "While" -> "As": the format's linking words are As / Then / Once.
> **story-critic:** The reveal must end on the bottle so the loop and the payoff meet.
> **shorts-format-critic:** Agreed.
>
> **Agreed:** anchor 5.2B; "While" -> "As"; end on the bottle.
> **Disagreed, settled:** fragments stay (owner's beat); names stay (series rule).
> **Owner decides:** the new last line, because it rewords his own.

Keep each turn to one or two lines. No turn without a reason.

## What to tell the owner
Two to four lines: the score (honest), the 2-3 fixes the critics agreed on, anything that touches his own wording (as a choice, not a change), and one question ("Shall I apply these three fixes?").
