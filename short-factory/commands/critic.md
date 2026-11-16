---
description: Run the expert panel on a script, title, hook or finished Short - shorts-format-critic leads on format, story-critic, hook-oracle and the episode's method critic advise; honest scores and the agreed fixes
argument-hint: '[episode slug or file] [rounds, max 5] [chat]'
---

Run the critics on: $ARGUMENTS

Follow the short-factory skill **sf-expert-panel**.

- Work out what to judge: an episode slug means its newest script version (or the locked script if locked, or the final video if the edit is done); a file path means that file; nothing means the newest script of the episode in progress (check `tracker.py status`).
- Rounds: the number given, otherwise 1; never more than 5. Stop on a plateau.
- Brief the critics with the material only, never our own opinion of it. Fresh agents each round, run in parallel: **shorts-format-critic**, **story-critic**, **hook-oracle**, plus the episode's method critic if one exists (the critic paired with the subject's study in `reference/creators/README.md` or the tracker's Skills & experts sheet, e.g. **stakes-ladder-critic**). Send **fact-checker** whenever the claims changed.
- If the arguments include "chat", also write the short critic chat (alternating turns citing rules, then Agreed / Settled / Owner decides).
- Keep only fixes two or more critics agree on (one is enough for a factual error). shorts-format-critic settles format clashes. A change to the owner's own wording is only ever a proposal.

Report the scores honestly (a round table, never rounded up) and the agreed fixes in plain English, no paths or code. End with one question: which fixes to apply.
