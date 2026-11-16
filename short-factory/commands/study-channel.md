---
description: Study a YouTube channel - download its top 10 Shorts and top 10 long videos, measure them, review them, then write its secret sauce and a new method skill and critic from it (named after the method, never the creator)
argument-hint: <@handle or channel URL> [key]
---

Study this channel: $ARGUMENTS

Follow the short-factory skill **sf-channel-study**, then **sf-secret-sauce**, in order. Read `${CLAUDE_PLUGIN_ROOT}/reference/lessons.md` first.

1. The first word of the arguments is the channel (@handle or URL); an optional second word is the short key to use. If nothing was given, show the top 3 of `reference/CHANNELS_TO_STUDY.md` (scored as in sf-secret-sauce) and ask which one.
2. Check the tracker first. If the channel is already analysed, say so in one line and ask whether to refresh; do not download again.
3. Do a list-only pass, tell the owner the channel's size and the 10 + 10 videos, and ask before downloading.
4. Download, measure, review (every item on the sf-channel-study checklist), and write the study notes, workbook and story-block chart.
5. Write the secret sauce, then LEARN: SECRET_SAUCE.md, a new `<method>-method` skill and a `<method>-critic` agent named after what the method does (never the creator's name), each with one source line at the bottom; record the pairing in the tracker and in `reference/creators/README.md`.
6. If downloads are blocked, do the light browser-only study and say clearly what could not be measured. Never get around a sign-in or bot check.

Nothing in this command spends credits. Talk to the owner in plain English, no paths or code, and end with one clear question.
