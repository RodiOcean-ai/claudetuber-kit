---
name: sf-channel-study
description: The /study-channel stage of the short-factory plugin - check the tracker, download a YouTube channel's top 10 Shorts and top 10 long videos, measure them (cuts, scene lengths, loudness, music share, sound effects, voice style, hooks, loops, titles, thumbnails), then Claude's own review of hooks, scripts as story blocks, music, visuals and packaging, and write the study notes, the workbook and the story-block chart. Use whenever the owner says "study this channel", "analyse @someone", "/study-channel", "download their top shorts", "how does X do it", "break down this creator", "measure their videos", "what are their hooks/titles/thumbnails like", or names a channel for the next episode that is not yet in the tracker.
---

# Channel study: download, measure, review, write it down

Goal: everything the next stage (skill **sf-secret-sauce**) needs to explain why this channel hits again and again. We study **techniques across the channel**, not one video's luck.

Read `${CLAUDE_PLUGIN_ROOT}/reference/lessons.md` first. Talk to the owner in plain English, no paths or code, one question at the end.

**Run tools as:** `"<python>" -I -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py" ...` with `<python>` from `config.json`. The studies folder (`studies_root`), study sizes and "delete media after" also come from `config.json`.

## Step 1. Tracker check (free, always first)
- `tracker.py status`, then look for the channel in the Channels sheet.
- **Already analysed?** Say so and stop, unless the owner wants a refresh (then only new videos are fetched; the downloader skips ids already in the tracker).
- Pick a short key (lower case, no spaces, e.g. `somechannel`). If it is new: `tracker.py add-channel ...` (see its help for the fields).

## Step 2. Download (free)
- First a dry look: `download_channel.py <@handle|url> --key <key> --list-only`. Tell the owner the channel's size, Shorts count and the top 10 + 10 by views. **Gate:** "Shall I download these 20?"
- Then: `download_channel.py <@handle|url> --key <key> --top-shorts 10 --top-longs 10`. It writes `shorts.json`, `videos.json`, `videos/<id>.mp4` with `info.json`, subtitles and the thumbnail, and `download.log` (the exact command used).
- Downloads are of public videos for private study only. Nothing downloaded ever goes into our video.

## Step 3. Measure (free, slow)
- `study_channel.py <key>` runs the analysers on every video, adds the loop check, title patterns and the thumbnail sheet, writes `<key> - all data.xlsx` in the study folder and marks the videos analysed in the tracker.
- Add `--skip-sounds` if time is short (the sound-effect detector is the slowest part). Add `--keep-media` only if Claude still needs to watch frames afterwards; otherwise big media (mp4, stems, mix wav) is deleted and the numbers, sheets and transcripts are kept.

| Measure | Tool | Where it lands |
|---|---|---|
| Views, length, upload date, title | `download_channel.py` | `shorts.json`, `videos.json`; workbook "Videos" |
| Cuts, shot lengths, scene-length list | `analyze.py` (via `study_channel.py`) | per-video `metrics.json`, `shots.jpg`; workbook |
| Loudness, voice above music, music share | `analyze.py` + `sounds.py` | `metrics.json`, `sounds.json`; workbook |
| Sound effects (count, type, timing) | `sounds.py` | `sounds.json`; workbook |
| Words, speaking speed, pauses, first line | `analyze.py` (Whisper words) | `transcript.json`; workbook "Hooks" |
| Voice style (pitch and speed movement) | `voice_style.py` | `voice_style.json`; workbook |
| Hook frames 0-3 s | `analyze.py` | `hook.jpg` per video |
| Loop (last vs first frame) | `study_channel.py` | workbook "Loop" |
| Title patterns (words, "?", "!", emoji, formats) | `study_channel.py` | workbook "Titles" |
| Thumbnails | `study_channel.py` | thumbnail contact sheet in the study folder |
| Story blocks per video | Claude writes json, `story_blocks.py` draws it | `reference/creators/<key>/story_blocks.json` + `.png` |
| Hook score | **hook-oracle** agent | study notes, workbook "Hooks" |

## Step 4. Claude's own review (the part the scripts can't do)
Look at the frames, transcripts and sheets yourself. For each item, write what you **see**, with counts ("6 of 8"), not impressions.

1. **Thumbnails:** one hero or many? faces or not? text words and colours; what makes the question. Compare against `reference/creators/documentary-thumbnails/NOTES.md`.
2. **Titles:** formats that repeat (e.g. "10 Ways to...", "with Emojis"), median word count, "?" vs "!", emoji, and the **median views per format** (a format is only a winner if its median is high, not its best one).
3. **Hooks:** for each Short, frames 0-3 s (what moves, by when), the first spoken or written line, and a **hook-oracle** score. Does it open on a "you" situation, a challenge, a statistic, a rule on screen?
4. **Music:** present or not, how loud under the voice, style and tempo, does it cut before punchlines.
5. **Sound effects:** how many per minute, which kind, where (first second? on cuts?).
6. **Scripts as story blocks:** for every Short with speech (and the opening of each long video), split the transcript into blocks and write one entry in `story_blocks.json`:
   `{title, views, duration, start_level, blocks: [[start_s, BLOCK, level_after], ...]}`
   with BLOCK one of HOOK, BELIEF, BUT, LADDER, TEASE, TENSION, SETBACK, COMEBACK, PAYOFF, LOOP. Then `story_blocks.py story_blocks.json story_blocks.png`. Count how many videos use each block.
7. **Speed:** words a second, a new picture every how many seconds.
8. **Transitions:** hard cuts, whips, fly-throughs, match cuts.
9. **Visuals:** live action or animation, set, colours, everyday objects or special ones, an on-screen "game board" (count, list, scoreboard).
10. **Scene lengths:** the longest and typical scene; how many tries/items per video.
11. **Loop:** does the end return to the start? measured seam vs a normal frame step.
12. **Captions:** words at a time, colour, position, built for mute or not.
13. **Long videos:** cold open, pivot lines, where the best payoff sits, sponsor placement, ending (one breakdown per video, like the shorts-format study's long-video notes).
14. **Contrast:** at least two of the channel's weaker videos in the same format, to show what the hits have that the misses lack.

## If downloads are blocked (light study, browser only)
When the downloader fails (sign-in wall, bot check), **do not try to get around it.** Do a light study like the one in `reference/creators/light-study/` (our first episode):
- Pull the Shorts list with views from the channel page (titles and view counts only).
- Open each top video in the browser **muted** and run the frame-sheet page script (`reference/creators/light-study/sheet.js`): 12-frame contact sheet, length, cut times, average shot, upload date and views.
- Note what can't be measured this way (loudness, music share, sound effects, voice) and say so in the notes. Never guess those numbers.

## Outputs
- `reference/creators/<key>/STUDY.md`: plain-English study notes, sections like the shorts-format study (big picture, Shorts recipe with a numbers table, hooks, script formula, footage, transitions, sound, captions, titles/covers, long videos, honest note).
- `reference/creators/<key>/techniques.md`: the on-screen techniques table with counts (like `reference/creators/light-study/techniques.md`).
- `<key> - all data.xlsx` (study folder; copy it into `reference/creators/<key>/`).
- `story_blocks.json` + `story_blocks.png`, hook sheets, thumbnail sheet.
- Then go straight on to **sf-secret-sauce**.

## Logging
- `tracker.py analysed <key>` when the review is done (the measuring script already marks each video).
- One dated line in `reference/creators/<key>/JOURNEY.md` (create it): what was downloaded, what was measured, what could not be, what the review found in one sentence.
- Tell the owner in 3-5 short lines: the channel, the 2-3 strongest patterns with counts, anything surprising, then one question ("Shall I write up the secret sauce?").
