---
description: Show where everything stands - channels studied, episodes in progress and their next step, posting slots, stats due, music rotation and credits spent - in plain English
argument-hint: '[optional: channel key or episode slug]'
---

Status: $ARGUMENTS

Run the tracker's status report with the Python named in `${CLAUDE_PLUGIN_ROOT}/config.json` (key `python`):
`"<python>" -I -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py" status`

If an episode slug or channel key was given, also read that episode's JOURNEY.md (episodes folder from `config.json`) or that channel's notes in `reference/creators/<key>/`.

Summarise for the owner in plain everyday English, short, with no paths, file names or code:
- channels studied, and which one is recommended next;
- each episode in progress: the stage it is at, the very next step, and who does it (him or Claude);
- posts scheduled, and any 24-hour or 7-day stat checks due now;
- the next music bed in the rotation;
- credits spent so far (total and per episode).

End with one clear question about what to do next.
