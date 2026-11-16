---
name: sf-posting
description: Posting and learning for short-factory Shorts - the post kit (title, description with credit and the "Not affiliated" line, hashtags, AI labels per platform, Made for kids No), the cover, the daily calendar (one post a day between 16:00 and 22:00 local time), scheduling through Metricool to YouTube Shorts, Instagram Reels, TikTok and Facebook Reels in one post (the video and cover go in by one-time Dropbox links; only after the owner's explicit OK for that post), logging the post, the 24-hour and 7-day stats with /log-stats, benchmarks, and the "our viral recipe list" after about 10 Shorts. Use whenever the owner says "post it", "schedule it", "post it at 21:00", "Metricool", "Dropbox", "posting kit", "title and description", "when should I post", "post plan", "/post-plan", "log the stats", "/log-stats", "how did it do", "24 hours", "7 days", "what's working for us", or when sf-pipeline reaches stage 8.
---

# Posting: the kit, the slot, the numbers

> **Claude schedules only with the owner's explicit OK for that exact post** (owner, 14 Nov 2026: "I want to fully automate this", then "you can post it as 21:00 for Facebook instagram tiktok and youtube"). A post goes out through **Metricool** (Step 4) once he has said, in the chat, which Short and when ("post it at 21:00", "Yes, schedule it"). An approved build, a finished video or an earlier OK for another Short is never that OK. Claude never logs into his accounts: Metricool and Dropbox are his own connectors.

Plain English to the owner, no paths or code, one question at the end.

**Run tools as:** `"<python>" -I -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py" ...` (`<python>`, the posting window and platforms from `config.json`).

## Step 1. Title (series formula)
- **A question + one emoji**, the same pattern across the series: "How Did 9 Videos Get 231,000 Subscribers? 🤯", "How Did Two Kids Get 13 Billion Views? 🤯".
- Keep the creator **anonymous** in the title ("two kids", "one faceless channel"); the video's last line reveals who.
- 4-8 words, the big number written as digits or a short word ("13 Billion"). Give the owner 3 options, the series-pattern one first. Run `topic_check.py` on the others.

## Step 2. The kit
- `post_kit.py <episode_dir> --title "..." --credit "..."` writes `post/POST.md` from the template, with the final video's facts (length, loudness, size).
- **Description:** one line that opens the question, then the credit line, then hashtags:
  > Two kids, eight shots, thirteen billion views. Here's the trick.
  > Credit: <channel name>. Not affiliated; analysis based on public data.
  > #shorts #youtubeshorts #contentcreator #animation #<topic>
- First names only for children. No real footage, thumbnails or logos in our video.
- **Settings on each platform** (spell them out in POST.md):
  - **AI label on:** YouTube "Altered or synthetic content" = Yes; TikTok "AI-generated content" on; Instagram "AI info" on.
  - **Made for kids: No** (the audience is creators).
  - No tag list on YouTube, no pinned "subscribe" comment (a pinned question is fine).
- **Covers:** `covers.py <video.mp4> [seconds ...]` makes candidate cover frames and a sheet. Pick a main and a backup (subject large, caption showing). The custom thumbnail comes from **sf-thumbnail**.
- One file works for YouTube Shorts, TikTok, Instagram Reels and Facebook Reels.
- **Cover:** the owner picks A or B (send him the covers side by side); the pick goes to the post as the video's cover.
- **Subtitles: skipped** (owner, 14 Nov 2026: "Skip subtitles"; Metricool cannot upload subtitle files). Make one with `subtitles.py <episode_dir>` (writes `post/<slug>.en_US.srt`, the name Facebook needs) only when he asks; he then uploads it in YouTube Studio > Subtitles.

## Step 3. The calendar slot
- `calendar_plan.py next <slug>`: the next free day, **one post a day, 16:00-22:00 local time** (the owner has been choosing **21:00**), with the reminder times for 24 h and 7 days. `calendar_plan.py list` shows the whole plan. A slot he moves by hand: change the row in the tracker's "Posting calendar" and the "## Slot" line in POST.md.
- Tell him the day and time and ask for his OK to schedule it (Step 4).

## Step 4. Schedule through Metricool (set up 14 Nov 2026)
**Accounts (your own):** a Metricool brand (`config.json` → `metricool`: your blog_id, your timezone, networks youtube, instagram, tiktok, facebook; on the free plan its own Google Drive link is locked). Dropbox (free Basic) through the **Dropbox connector**, plus **Dropbox for desktop** syncing your Dropbox folder on this PC. Check once per session: Metricool `getBrandSettings` shows the four networks and your timezone.

**Only after his OK for this post**, in this order:
1. `metricool_prep.py <episode_dir> --date YYYY-MM-DD --time HH:MM --cover A --publish public` (try `--dry` first). **`--publish public` only for this one post and only after his OK for it**; without it the file is safe by default (autoPublish off, YouTube private, TikTok only me: nothing goes out publicly by itself), and `--publish unlisted` gives an unlisted YouTube copy. Read him the script's "WILL HAPPEN" line before step 4. The script copies `post/<slug>_FINAL.mp4` and the cover into `Dropbox\<dropbox_folder from config.json>\<date> <slug>\`, and writes `post/metricool_post.json`: the whole post with `<VIDEO_LINK>` and `<COVER_LINK>` placeholders. One post for all four networks: caption = title line + the POST.md description (story, credit, "Not affiliated", hashtags with #shorts); titles for YouTube, TikTok and Facebook; YouTube type short, madeForKids false, isAiGeneratedContent true; Instagram REEL isAiGenerated true; TikTok isAigc true; Facebook REEL; autoPublish, YouTube privacy and TikTok privacy as `--publish` set them.
2. Dropbox `get_file_metadata` on both `dropbox_paths` until each exists with the printed size (a 35 MB video takes under a minute). Don't use `sleep` over about 25 s in the shell; check again instead.
3. Dropbox `download_link` on both paths, `expiration_in_sec` 900. The connector **cannot make public links** (`create_shared_link` is private only); these one-time links are the way. Each works once and for 15 minutes, so make them right before step 4, and make new ones if a call fails.
4. Put the two links in place of the placeholders and call Metricool `createScheduledPost` with the file's `blogId`, `date` (with the UTC offset) and `info`. Metricool copies both files into its own storage on the spot.
5. **Check:** the response's `media[0]` and `videoThumbnailUrl` now point at static.metricool.com; a HEAD request on each must show the same byte size as ours. All four providers show `PENDING`. If anything failed, nothing was posted: fall back to the upload folder (video, cover, CAPTIONS.txt) and tell him.
6. Record it: the "Posting calendar" row stays `planned` with the time; a dated JOURNEY line with the Metricool post uuid; tell him the day, time, networks and the post's `plannerUrl`.
7. After the slot: Metricool `getScheduledPosts` no longer lists it once it has gone out; then `tracker.py log-post <slug> "<platform>" "<YYYY-MM-DD HH:MM>"` for each of the four platforms.

**Covers and the related video (owner, 14 Nov 2026: "the video was published without thumbnails - also can we add the related video in youtube?")**: Metricool's cover only shows on YouTube Shorts if YouTube allows custom Shorts thumbnails for the channel (from July 2026 only for Partner Program channels, on desktop); otherwise the owner picks a FRAME in the YouTube app (open the Short, Edit, choose the cover frame). TikTok ignores the cover on personal accounts (it needs a TikTok Business account). The Short's "Related video" link (it sends viewers to another video of the channel) cannot be set through Metricool or the YouTube API: the owner sets it in YouTube Studio (Content, Shorts, the Short's details, Related video) or in the YouTube app; suggest the best-performing related Short of the series. Claude must not spend vidIQ credits on thumbnail writes without his OK for that exact call.

**To change or cancel** a scheduled post: `getScheduledPosts` for its id and uuid, then `updateScheduledPost` with the FULL original content plus the change (it replaces the whole post; there is no undo). Only on his request.

First two posts this way (14 Nov 2026): cleaning (Sat 21:00) and light switch (Sun 21:00), all four networks; the stored files matched ours to the byte.

## Step 5. Stats at 24 hours and 7 days (/log-stats)
- **First try Metricool:** `getAnalyticsAvailableMetrics` (network youtube / instagram / tiktok / facebook) for the metric ids, then `getAnalyticsDataByMetrics` for the day range. Where it lacks a number (YouTube's "viewed vs swiped away" is usually Studio-only), ask the owner for it from YouTube Studio (Shorts analytics): **views**, **"viewed vs swiped away"** (the % who stayed), **average % watched**, **subscribers gained**.
- `tracker.py log-stats <slug> 24 --views N --stayed PCT --avg-pct PCT --subs N` (and `168` for 7 days).
- Then judge honestly, in one or two lines, against the benchmarks:

| Benchmark | Number |
|---|---|
| The faceless-channel study's winners (its 24 h rule) | **80 %+ stayed**, retention about 90 %+ |
| Our episode 1 (recipe, flat 2D) | 1,114 views in 48 h, 61.4 % stayed |
| Our "9 videos" episode (faceless-channel study, 3D) | 1,262 views in about 3.5 h, 66.8 % stayed |
| Newer numbers | see the Performance sheet and `reference/lessons.md` ("Measured so far") |
| Long videos (a former lead editor of a top channel) | under 60 % still watching at 30 s = a problem; 70 %+ = great |

- Judge at 24 h; don't wait for a flop to "warm up". If "stayed" is low, the hook or the cover is the leak (run **hook-oracle** on the real first 3 s). If stayed is good but average % watched is low, the middle sags.
- Add each new result to "Measured so far" in `lessons.md` (one line per episode).
- **Easter egg check at 7 days:** count comments that mention the hidden water bottle (or ask "where is it?"). If fans find it, keep it; if nobody does after 3 episodes, make it a little easier to spot.

## Step 6. Our viral recipe list (after about 10 Shorts)
- Sort our Shorts in the Performance sheet by 24 h "stayed" and 7 d views. Re-watch the top 3 and the bottom 3.
- Write `reference/OUR_VIRAL_RECIPE.md`: what the winners share (hook type, length, scene speed, music bed, thumbnail style, topic type, reveal), what the losers share, each with counts.
- Put the 3-5 strongest rules into `lessons.md` and use them in sf-pipeline stage 1 and 3. **Redo it whenever views drop**: recipes decay.

## What to tell the owner
"Kit ready: title, description with credit, AI labels on, Made for kids No, cover A. Next slot: Tuesday 21:00 on YouTube, Instagram, TikTok and Facebook. Shall I schedule it in Metricool?" After his OK and the check: "Scheduled for Tuesday 21:00 on all four; Metricool has the full video and the cover." At 24 h: the Metricool numbers, plus "Could you send me the 'viewed vs swiped away' number from YouTube Studio?"
