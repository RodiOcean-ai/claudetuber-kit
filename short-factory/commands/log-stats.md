---
description: Log a Short's 24-hour or 7-day numbers (views, viewed vs swiped away, average % watched, subscribers) in the tracker and judge them against our benchmarks
argument-hint: <episode slug> <24|168> [views stayed% avg% subs]
---

Log stats: $ARGUMENTS

Follow the short-factory skill **sf-posting**, step 4.

1. Arguments: the episode slug, the checkpoint (24 = 24 hours, 168 = 7 days), then the numbers if given: views, "viewed vs swiped away" %, average % watched, subscribers gained.
2. If any number is missing, ask the owner for it in one short message (say where it is in YouTube Studio's Shorts analytics) and wait.
3. Record it: `tracker.py log-stats <slug> <hours> --views N --stayed PCT --avg-pct PCT --subs N`, plus a dated line in the episode's JOURNEY.md.
4. Judge it in two or three plain lines against the benchmarks (the faceless-channel study's winners: 80 %+ stayed; our earlier episodes under "Measured so far" in `reference/lessons.md`): what the number means and the most likely leak (the hook or cover if "stayed" is low; the middle if average % watched is low). Add the result to "Measured so far".
5. If this is about the 10th Short with logged stats, offer to write our viral recipe list.

No paths or code in the reply; end with one question.
