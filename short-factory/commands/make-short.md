---
description: Make the next Short in the "How did X get Y?" series - from subject and title through facts, script and critics, voice, 3D, edit, thumbnail and posting plan, with an owner gate after every stage
argument-hint: '[channel key, topic or episode slug to continue]'
---

Make (or continue) a Short: $ARGUMENTS

Follow the short-factory skill **sf-pipeline** stage by stage. Read `${CLAUDE_PLUGIN_ROOT}/reference/lessons.md` first.

- If the argument is an existing episode slug (check `tracker.py status` and the episodes folder from `config.json`), read its JOURNEY.md, say in one line where it stands, and continue from the next unfinished gate.
- If it is a studied channel key, start at stage 1 with that channel's secret sauce.
- If it is a channel that has not been studied, offer `/study-channel` first.
- If it is empty, show the studied channels not yet made into an episode and ask which one.

Hard rules: one stage at a time, and stop at each gate for the owner's yes. Claude builds and prices paid nodes with `estimate_only` only; the owner presses Generate. The voice is made in-house and free with voice_make.py (the owner picks the take by ear). Nothing is rendered before the owner approves the build on the localhost review page, and a post is scheduled (through Metricool) only after his explicit OK for that post. Log every stage in the episode's JOURNEY.md and the tracker. Plain English to the owner, no paths or code, one clear question at the end.
