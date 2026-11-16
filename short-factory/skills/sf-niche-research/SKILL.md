---
name: sf-niche-research
description: Find what already works in our niche and copy the reason it works - our niche in simple words (Shorts that take apart a big YouTube channel's strategy - titles, thumbnails, hooks, storytelling, music, sound effects, volume), the depth-first "demand map" (10 common search lines -> standout videos -> their channels -> each channel's standout video -> recommendations -> repeat) run with niche_map.py, a research database, who else makes videos like ours, which title/thumbnail/structure formats win and WHY, positive and negative evidence, and how a winner is doubled down on. Learned from a public YouTube training (Sep 2026). Use whenever the owner says "research the niche", "who else does this", "what works in our niche", "find outliers", "demand map", "search lines", "standout videos", "what should the next episode be", "copy what works", "double down", or before sf-pipeline stage 1 when no subject is chosen.
---

# Niche research: find what works, copy why it works

From a public YouTube training video (1.0M views, Sep 2026; see the source line at the bottom). Full notes: `${CLAUDE_PLUGIN_ROOT}/reference/methods/youtube-training-notes.md`. Read `reference/lessons.md` first.

**Copy the reason, never the identity:** take a format's psychology, structure and pacing; never another channel's name, face, footage, mascot or exact title. **This skill spends nothing.** Plain English to the owner, no paths or code, one question at the end.

## Our niche in simple words (never drift from it)
This is the kit author's own niche. For your own channel, use the niche sentence in `assets/brand/BRAND.md` (skill **yt-niche** writes it) wherever this section says "our niche".

> **We make 30-second 3D Shorts that take apart how a big YouTube channel grew: its titles, thumbnails, hooks, storytelling, music, sound effects and volume.**

Every episode critiques a channel's **craft**. The channel is one campaign; each Short is one ad in it. An off-topic hit brings viewers who ignore the next ten Shorts, so a tempting idea outside this sentence gets a "no" or a bridge back to it.

**The breakdown checklist** (what every episode and every study looks at, in this order): title, thumbnail, hook (first 3 s), story structure (Save the Cat / Problem-Agitation-Solution / Hero's Journey / And-But-Therefore; skill **sf-story-craft**), villain, music, sound effects, volume (voice above music).

## Step 1. Seed list (free)
- Write **10 search lines** our viewers would really type (their words, not ours): e.g. "how did <a famous creator> get famous", "why this youtube channel blew up", "secret of viral youtube shorts", "youtube hook examples".
- Save them as `seeds.txt` in `<studies_root>/niche_<name>/`. Keep old seed files; add new lines when a branch reveals new words people use.

## Step 2. The demand map (free, about 10-20 minutes)
```
"<python>" -I -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/niche_map.py" <name> --seeds <seeds.txt> [--per-search 20] [--per-seed-channels 3] [--max-channels 30] [--min-views 100000] [--x 3]
```
It runs the depth-first search with a **stack** (a to-do pile; the newest find is explored first):
1. Pop a search line -> Shorts search + normal search -> push every result over the minimum views.
2. Pop the biggest **on-topic** video (title shares a word with the search line or our topic words) -> open its **channel** (Shorts and long videos) -> work out that channel's normal (median) views -> mark its **standouts** (3x its own median or more).
3. A channel already opened = branch done, **step back**; each search line opens at most 3 new channels, so all 10 lines get explored.
4. Writes `niche_map.xlsx` (Searches, Videos, Channels, Standouts, Stack: every step in order) and `NICHE_MAP.md`.
- **Recommendations** are not in its lists. Open the top 5-8 standouts in the built-in browser (muted), note the "up next" videos that look like ours, and add their channels by hand (or as new seed lines) and run again.
- If YouTube answers "too many requests", wait and rerun later; never get around a sign-in or bot check.

## Step 3. Claude's review (the part the tool can't do)
For the top standouts and the channels closest to us, write `REVIEW.md` in the dated folder:
1. **Who else does what we do?** Channels that break down creators or YouTube strategy: size, Shorts vs long, how often they post, what they cover. Mark the 3 nearest rivals.
2. **Winning formats** (titles, thumbnails, structures). For each: how many standouts use it, the median views, and **why it works for this audience** (the promise it makes). A format only counts if it repeats; one viral video is a clue, not proof.
3. **Negative evidence:** the same format on videos that flopped, and what they did differently (the training: the "I made 300 videos and learned this" title only worked with its 20-40 point structure).
4. **Copy the whole package:** title + thumbnail + structure + delivery style together, never the title alone.
5. **Awareness bridge:** what outcome do viewers already want ("go viral", "get subscribers")? Package that outcome; reveal our mechanism (the craft) inside.
6. **Gaps:** what nobody in the niche does yet (our 3D world, measured numbers, the creator reveal at the end).
7. **Next subjects:** channels that keep showing up as standouts become candidates in `reference/CHANNELS_TO_STUDY.md` (scored as in **sf-secret-sauce**).

## Step 4. Packaging check before any episode is locked
- **Promise:** title and thumbnail make one promise together, readable in one glance.
- **Beside the feed:** put our thumbnail and title next to the 5 nearest standouts (a mock-up sheet) and ask: would the right viewer pick ours? If not, revise.
- **Promise, proof, plan** in the first seconds: repeat the promise, show why to believe us, show where it goes. In a Short this is one or two lines (the hook and the "But").
- **Satisfaction beats retention:** the payoff must over-deliver on exactly the title's promise.

## Step 5. Double down with our own data
After the 24 h and 7 d stats (`/log-stats`):
- Ask **why** the winner worked (subject? title format? hook? the creator's fame?). Keep that reason and find a new way to use it; never just remake the same video.
- Diagnose the drop: few views = packaging; swiped away early = hook; low % watched = story; views but no subscribers = off-niche viewers.
- Rerun the demand map every ~10 episodes or when views drop; the niche moves.

## What gets written down
- `<studies_root>/niche_<name>/<date>/`: the workbook, `NICHE_MAP.md`, `REVIEW.md`.
- One dated line in `reference/lessons.md` for each new rule the review proves (with counts), and new candidates in `CHANNELS_TO_STUDY.md`.

## Tell the owner
3-5 lines: the 3 nearest rivals and their size, the 2-3 winning formats with counts and why they work, the gap we can own, then one question ("Shall I add X to the study list?").

Source: our own notes on a public YouTube training by Jake Trinder ("The Most Valuable YouTube Training You'll Ever Watch"). Not affiliated with or endorsed by Jake Trinder.
