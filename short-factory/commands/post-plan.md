---
description: Prepare the posting kit and the next daily slot (16:00-22:00 local) for a finished Short and, after the owner's OK, schedule it through Metricool on YouTube, Instagram, TikTok and Facebook; or show the posting calendar
argument-hint: '[episode slug | list]'
---

Posting plan: $ARGUMENTS

Follow the short-factory skill **sf-posting**.

- `list` (or nothing): run `calendar_plan.py list` and tell the owner, in plain English, what is scheduled, what is ready but has no slot, and which 24-hour or 7-day stat checks are due.
- An episode slug: check the final video exists and passed the format check; make or refresh the post kit (title options in the series pattern, description with credit and "Not affiliated; analysis based on public data", hashtags, AI labels per platform, Made for kids No, covers), then `calendar_plan.py next <slug>` for the slot.

Then tell the owner the day, time and networks and ask for his OK. Only after his explicit OK for this post, schedule it through Metricool (sf-posting Step 4: `metricool_prep.py`, one-time Dropbox links, `createScheduledPost`, then check Metricool stored the full video and cover). If Metricool or Dropbox fails, give him the upload folder instead. Log it with `tracker.py log-post` once it has gone out. Plain English, no paths or code, one question at the end.
