# Short Factory

A helper for Claude that runs our whole Shorts routine in one place: pick a channel, study why it keeps going viral, learn its "secret sauce", turn that into our own 30-second 3D Short, and post one a day. Everything is written down in one Excel workbook, so nothing is studied twice and every result is kept.

## The two big commands

**/study-channel** followed by a channel name (for example `/study-channel @somechannel`)
- Claude checks the workbook first. If we already studied that channel, it says so and stops.
- It shows you the channel's 10 most-viewed Shorts and 10 most-viewed long videos and asks before downloading.
- It measures them: length, how fast they talk, how often the picture changes, music and sound effects, hooks (the first 3 seconds), titles, thumbnails, whether the video loops.
- Then it watches and judges what the numbers can't show, and writes up the secret sauce: what repeats in their hits, what is just luck, what we copy and what we don't.
- Finally it learns it: a new method guide and a matching critic that checks our scripts against that recipe. Both are named after what the method does, never after the creator, and carry one source line naming the channel studied.
- The big video files are deleted afterwards; the numbers and notes are kept.

**/make-short** (optionally with a channel or an episode name)
Eight steps. After each one Claude stops and asks you.
1. Subject and title (series style: a question plus one emoji; the creators stay anonymous until the last line).
2. Facts, each checked in two sources.
3. Script, reviewed by the critic panel (the format critic leads on format). Your wording always wins.
4. Voice: you make the takes in ElevenLabs, Claude stitches the best bits together.
5. The 3D world in Blender: test pictures first, then the full render.
6. The edit: captions, music, whooshes, loudness, and an 11-point check against the format benchmark's numbers. You get a phone copy.
7. The thumbnail.
8. The posting kit and the day and time to post.

## Method guides and critics (from our own channel studies)
Each one is named after what it does, not after anyone:
- **Guides:** `shorts-format` (the measured 30-second explainer format) and `what-if-longs` (5-12 minute "what if" videos); `channel-playbook`, `story-scripts`, `natural-ai-voice`, `video-editing` and `thumbnail-design` (a faceless AI channel's craft); and the Short recipes `stakes-ladder-method`, `game-drama-method`, `everyday-object-method`, `trick-shot-method`, `guess-and-reveal-method`, `curiosity-gap-method`, `verdict-method`, `creator-breakdown-method`, `survival-story-method`, plus `packaging-method` (title, thumbnail and first seconds).
- **Channel basics for beginners:** `yt-niche` (find your niche), `yt-branding` (name, logo, banner, colours, fonts, mascot and voice in one brand sheet, `assets/brand/BRAND.md`), `yt-titles` (titles that get clicked without lying) and `yt-thumbnails` (one-glance thumbnails, phone check).
- **Critics:** `shorts-format-critic` (leads on format), `story-critic`, and one critic per recipe (`stakes-ladder-critic`, `game-drama-critic`, `everyday-object-critic`, `trick-shot-critic`, `guess-and-reveal-critic`, `curiosity-gap-critic`, `verdict-critic`, `creator-breakdown-critic`, `survival-story-critic`, `packaging-critic`). They are checklists built from our measurements, not personas.
- Which channel each was studied from is in `reference/creators/README.md` and in one source line at the bottom of each guide and critic. Independent analysis of public videos; not affiliated with or endorsed by any channel named there.

## Two new helpers (4 Nov 2026)
- **Niche research:** Claude types the 10 searches our viewers would type, finds the videos that beat their own channel's normal views, opens those channels and their standout videos, and writes a map of who else does what we do and which formats win (and why).
- **Story craft:** before the critics, every line of a script must have a job, there is a villain (an obstacle, never a real person), and the ending comes back to the start with a twist.

## Smaller commands
- **/status**: where everything stands, in plain English.
- **/critic**: run the critic panel on a script or a finished Short.
- **/post-plan**: the posting kit and the next free slot, or the whole posting calendar.
- **/log-stats**: record a Short's numbers after 24 hours or 7 days.

## What you press (and Claude never does)
- **Generate** in ElevenLabs and ElevenCreative. Claude builds the boards and shows you the price; you decide and press.
- **The voice takes**, in ElevenLabs Text to Speech.
- **Upload and Schedule** in YouTube Studio (and posting on TikTok and Instagram).
- **Yes or no** at each step.

## Where things go
- **Channel studies:** the studies folder you set in `config.json` (`studies_root`; one folder per channel).
- **Episodes:** the episodes folder you set in `config.json` (`episodes_root`; one folder per Short, with its own diary of every decision, called the journey log).
- **The finished Short, thumbnail and posting notes:** the "post" folder inside each episode.
- **What we learned about each creator:** the "reference" folder in this plugin.
- **The tracker workbook:** the "data" folder in this plugin.

## The three music beds
Every Short uses one of our own three background tracks, in turn: **sprint, then clocks, then steps**, then back to sprint. Claude places the track so its last big hit lands on the last word and the very first frame sits on a beat. The workbook remembers which one was used last.

## Daily posting
One Short a day, between **16:00 and 22:00** your time. Claude suggests the slot and prepares the title, description (with credit to the creator and "Not affiliated; analysis based on public data"), the AI label settings and "Made for kids: No". You upload and press Schedule. After 24 hours and after 7 days, Claude asks you for four numbers from YouTube Studio: views, "viewed vs swiped away", average % watched and subscribers. After about 10 Shorts, Claude writes our own "viral recipe list" from what worked best.

## The tracker workbook
One Excel file with a sheet for each of these: channels, videos analysed, patterns, secret sauce, skills and critics learned, episodes, music rotation, posting calendar, performance (24 hours and 7 days), and credits spent per episode.

## Safety rules (always on)
- Claude **never spends your ElevenLabs credits** or money on any other paid service. It builds and prices; you press Generate. A built-in guard blocks it even if asked.
- **No real faces** and no AI copies of real people, children above all: silhouettes from behind and faceless toy figures.
- The creators stay **anonymous in the hook and on the thumbnail**; the last line reveals who they are.
- Every claim has **two sources**.
- Claude posts **only with your OK for that exact post** (through Metricool, with the video sent by a one-time Dropbox link), renders nothing before you approve the build on the review page, and never saves over an original Blender file.
- Downloaded videos are only for study; nothing of theirs goes into our videos.
