---
name: sf-pipeline
description: The /make-short orchestrator of the short-factory plugin - takes one studied channel (or a topic) all the way to a finished, posted 30-second 3D explainer Short in our "How did X get Y?" series - subject and title, facts, script with the expert panel (the format critic leads), voice comp, 3D in our underwater lab (Blender, blocky cast), Remotion edit with rotating music, GPT-image-2.5 thumbnail, post kit, daily calendar slot and 24 h / 7 d stats - with an owner gate after every stage and a tracker entry for everything. Use whenever the owner says "make a short", "next episode", "make the <channel> short", "/make-short", "turn the study into a short", "what's the next step on the episode", "carry on with the short", or names a channel he wants the next Short about.
---

# Short factory pipeline: one Short, eight stages, eight gates

This skill runs the whole episode. Each stage below says what Claude does, which tool, skill or agent does it, what the owner decides (the **gate**), and what is written down. Nothing moves to the next stage until the owner says yes.

Read `${CLAUDE_PLUGIN_ROOT}/reference/lessons.md` before starting. Every rule there came from the owner or from a mistake we paid for, and it wins over anything in this file.

## How to run the tools
- Every script lives in `${CLAUDE_PLUGIN_ROOT}/scripts`. Run it with the Python named in `config.json` (key `python`):
  `"<python>" -I -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py" ...`
- Paths (episodes folder, studies folder, ffmpeg, Blender, fonts, posting window, music rotation) all come from `config.json`. Never hard-code them.
- Episode folder: `<episodes_root>/<slug>/`, made by `new_episode.py <slug>`. It holds `voice/`, `takes/`, `blender/`, `edit/`, `post/`, `JOURNEY.md` and `facts.md`.
- The master workbook is `data/tracker.xlsx`, written only through `tracker.py`.

## Series rules ("How did X get Y?")
1. **Critique the channel and its techniques**, never one video's statistics. One record clip can be an example inside the story, not the story.
2. **The creators stay anonymous** in the hook and on the thumbnail ("two brothers", "one faceless channel"). **The last line reveals who they are.** The reveal is part of the reward.
3. **No real faces, no AI likeness of real people**, children above all: silhouettes from behind, faceless toy figures.
4. Credit the creator in the description, with "Not affiliated; analysis based on public data". First names only for kids. No real footage, thumbnails or logos in our video.
5. **The shorts-format study is the format authority for Shorts.** Other critics advise; its measured rules settle arguments.

## The 1-to-1 method (owner, 11-12 Nov 2026; every Short from the squirrel episode on)
Where this section and an older line further down disagree, **this section wins**. It is how the squirrel episode was made ("Ex-NASA Engineer's $5M Video Lost to a Squirrel", from the engineering-stunts study), after the owner said "we lose the tone battle, [the format benchmark] always wins" and "let's generate a script 1 to 1 like [the benchmark's] videos and then understand how to reach perfect editing".

1. **Pick one Short from the format benchmark as the model** (the owner may name it). If it is one of its top 100, its skeleton is already measured in `reference/creators/shorts-format/top100/library.json` (story type, glue words, first "But", ending); see `skills/shorts-format/references/top-100-scripts.md`. Otherwise download it for private study, measure it (`analyze.py`, `voice_style.py`): seconds, words, the sentences with their word counts and the job each does, the delivery sentence by sentence, the framings every half second. First model: "Why Your Brain Focuses On Negative Things" (38 s, 100 words, 8 sentences of 11, 9, 5, 15, 10, 21, 14, 15 words): one person does one odd thing -> a question -> the obvious answer -> "But" -> what nobody saw -> the meaning in one example -> "Because ..." -> "Meaning ..." returning to the first picture and speaking about "us".
2. **Write ours sentence for sentence:** the same number of sentences, the same length each (within 1-2 words), the same job each, the same linking words ("Then", "But", "Because", "Meaning"). Flowing sentences of 10-21 words, never fragments or "X. Y. Z." triplets. Show the owner the two scripts side by side in a table. **The last line gets the most care:** offer three endings of about 15 words; expect him to write his own. His wording wins.
3. **Facts still hold:** every claim two sources; say what the hits share and what the weak one lacks, never the cause; a "Because ..." line that is a principle and not a measurement is said to him plainly. **Count every headline number twice** from two places before telling him.
4. **Voice:** the WHOLE script in ONE node (American Explainer, eleven_v4), one calm mood, tags only where the model's delivery really changes ([calm] at the start, [curious] on the "But" line, [thoughtful] on the example), no CAPS. A free local draft voice first (VibeVoice) so he hears the flow. He generates 2-3 takes. **Finish = one fixed volume and nothing else** (no cuts, no added silence, no loudness normalising; never place a cut from Whisper's word times). Check: `voice_check.py <wav> format-real` (the benchmark's real ranges), aim 9 of 9.
5. **Picture: the story is acted out in 3D. No boards, no numbers, no labels, no real clips; only captions.** One framing about every 1.5 s, each showing exactly the words being said and landing on the word; **every named thing gets its own framing on its own word** (a list of three = three framings); each character must read as what the word says at a glance. The action is already happening on frame one. Halfway, the picture may leave the lab for the plain space (`place void`) to act the meaning out; the last line returns to the first picture. Narrator off screen: no lip rows except when our host speaks as "I".
6. **Build order:** shot plan table (model's framing | ours) -> scene tables from the word times -> `MODE=check` -> look at one still per framing YOURSELF and fix them -> full render with `scripts/render_parallel.py` (6 workers, about 80 s for 17 s of lab) -> edit -> **send him the video**. He judges video, not stills: after "build it" do not stop to ask at the stills.
7. **Edit:** captions small and low (62 px, 2-3 words, about y 1400); **no ping**; the sea wave at most once, as the fast right-to-left wipe; music about 18-19 LU under the voice; a soft pop only on a real physical hit; `format_check.py` 11 of 11.
8. **Look:** do all checks, stills and timing fixes in the normal look; render the approved cut last with `LOOK=chess` (marble checker floor, dusk sky, warm key and cool rim, polished metal; about 2-4 s a frame, 4 workers). The owner's bar is the chess Short ("our only hit so far"); `LOOK=premium` was rejected as "still not like the chess".
9. **Packaging:** three titles; two thumbnail pictures with the excited toy face; he picks the picture, then the word from **options rendered on the picture**. Give him the post kit text in the chat and open the folder for him.


## The format spine (every script)
"You" situation (never a statistic) -> wrong belief -> **"But"** twist at 5-9 s -> escalation ladder -> payoff (scale surprise, reveal or human sting) -> loop back to the opening. Top-100 refinement (12 Nov 2026, `shorts-format/references/top-100-scripts.md`): name the story type first; the first "But" lands at a median 9 s (6-13 s) and only flips, stories and ladders need it; every sentence after the first opens with a glue word or points back; a cold open mid-action is fine for true stories. A setback/comeback is optional (3 of the benchmark's top 10). 75-95 words, about 2.8 words a second, voice on frame one, no pause over 0.5 s, 0-2 numbers is the benchmark's habit (we allow up to 4), captions 1-3 words.

## The eight stages

### 0. Niche research (every ~10 episodes, or when no subject is chosen)
- Skill **sf-niche-research**: our niche in one sentence, the 10 search lines, `niche_map.py` (standout videos -> channels -> their standouts), Claude's review of who else does this and which formats win and why. Winners become candidates in `CHANNELS_TO_STUDY.md`.
- **Gate:** the owner picks which candidate to study.

### 1. Subject, angle and title
- Stay inside our niche sentence (sf-niche-research): every episode takes apart a channel's craft (title, thumbnail, hook, story, music, sound, volume).
- Pick the subject from the tracker (Channels sheet: studied, secret sauce written) or from what the owner names. If the channel has not been studied, offer `/study-channel` first.
- Write 3-5 angles that critique the channel's **techniques**, each with a series title: question + one emoji ("How Did Two Kids Get 13 Billion Views? 🤯").
- Run `topic_check.py "title" ...` against the format benchmark's titles (default key `shorts-format`) and again with `--channel <study_key>` against the subject's own. Drop anything TOO CLOSE.
- Score the titles with **packaging-method** (max loading, rhythm, 3 focal points, not a summary, outsider pull); keep one series-pattern title and one claim version for the owner.
- After the owner picks: `new_episode.py <slug>`, then `tracker.py add-episode <slug> ...` (see its help for the fields).
- **Gate:** the owner picks the angle and title.

### 2. Facts
- Send the **fact-checker** agent every claim the angle needs. Each claim needs **two sources** in `facts.md`; uncertain items go in an "uncertain, not in the script" list.
- **Gate:** none, but tell the owner plainly what could not be confirmed.

### 3. Script and the expert panel
- Write the script on the format spine (skill **shorts-format**, stage 4) plus the subject's secret sauce (`reference/creators/<study_key>/SECRET_SAUCE.md`) and the episode's **method skill** if one exists: the skill paired with the subject's study in the table in `reference/creators/README.md` or in the tracker's Skills & experts sheet (e.g. **stakes-ladder-method**). Use **story-scripts** for the planted question and the human-writing pass.
- Apply the **survival-story lens** from **survival-story-method** (owner, 6 Nov 2026): hero + clock in line 1, what's lost by 5-9 s, 3 links that cause each other, one setback at about 18-22 s, a last line that returns to frame one changed.
- Run `script_check.py <script.txt>` until clean.
- Run skill **sf-story-craft** before the panel: structure picked by the feeling, a villain, a job for every line (no job = cut), everything planted is paid off, and a bookend ending with a twist. Its changes are proposals when they touch the owner's wording.
- Run the panel with skill **sf-expert-panel**: **shorts-format-critic** leads and has the final say on format; **story-critic**, **hook-oracle** and the episode's **method critic** (paired with the subject's study the same way, e.g. **stakes-ladder-critic**) advise. Max 5 rounds, stop on a plateau, keep only fixes two critics agree on, the owner's own wording wins.
- **Gate:** the owner approves. Save the approved text as `script_LOCKED.txt` and write "Script LOCKED: vN" in JOURNEY.md.

### 4. Voice: the IN-HOUSE voice (free, from 14 Nov 2026)
The owner dropped the ElevenLabs takes for a free local voice after five blind listening rounds ("Lets use voice 1 method - its not perfect but it usable"). What he heard as "not crisp" was the DELIVERY ("Flat, low energy"; ElevenLabs "emphasis some where or part of words"), not the sound: EQ, super-resolution, an enhancer and a radio-style finish all failed by ear.
- Write `voice_script.txt` as before (one piece, `B01: [calm] ...`, sound-spellings such as "Kahbee Lahmeh", no CAPS). Mood tags are dropped by the tool; the read stops on the locked script's last word, so there are no read-on words to cut.
- `"<python>" -I -X utf8 scripts/voice_make.py <episode> --takes 2` (`--dry` first shows the sentences). It reads each sentence with **Chatterbox copying a LIVELY sample** (`assets/voice/channel_lively.wav` from the ice take, or `--lively assets/voice/channel_lively_cleaning.wav`; exaggeration 0.75, cfg 0.4), joins them with 0.3 s pauses, and finishes with `tools/voice_polish.py` (tone matched to the ElevenLabs takes). The card part goes through the traffic light; the finish and the Whisper word check run on the processor. About 1.5 minutes a take. Never time-stretch it.
- **No voice swap and no ClearerVoice rebuild by default** (owner, 14 Nov 2026: "There is such a weird ecco to the voice", then "All of the voices have a weird ecco - something is wrong"): the rebuild left a haze after every word (lingering -9.7 dB vs ElevenLabs -14.4) and every voice built with the swap (Chatterbox VC) echoed to his ear although no measure caught it. Both stay as options (`--swap`, `--finish sr`) only for tests.
- Its printout per take: length, words a second, % of words matching the script, the last word. A take must say every word and end on the script's last word (one VoxCPM2 read once dropped "ticking").
- **Gate:** the owner picks a take by ear (put both on a listening page next to the last approved voice). Then `voice_make.py <episode> --use N` makes it `voice/final_voice.wav` + `.words.json` (the old one is kept as `final_voice_before.*`).
- Known limits (owner: "not perfect"): a little less like the original speaker than ElevenLabs, fixed 0.3 s pauses between sentences. Tools tried and kept for later: VoxCPM2 (`tools/voxcpm2`: 48 kHz, voice design from a description; its reads started every sentence with a breathy hiss, trim it), ClearerVoice's enhancer, Qwen3-TTS (sounded like a different speaker).
- The older way, if the owner ever asks for ElevenLabs again: he generates 2-3 takes on a one-node board Claude builds and prices; pick with `voice_check.py <take.wav> format-real`; log the credits.

### 5. 3D world: THE LAB by default (skill **sf-blocky-world**, place `lab`)
- **Every Short is set in our underwater lab** (owner, 10 Nov 2026: "Yes, lab by default"): the channel's own world, light
  blue, the blocky cast with this episode's restyled hero, and the HUGE screen behind them showing what the video is about
  (`screen:` a restyled board from `boards_9x16/`, a chart or a clip; it changes with the story). Scene lines `light: underwater`,
  `screen: ...`; the lab's things (crates, lifebuoy, sub) come with it. The older one-world toy look (**sf-blender-world**)
  only when the owner asks for it; a creator method's "Stage 5" notes still apply inside the lab.
- Scene plan from the word times: a new framing about every 1.5 s that shows the words being said and lands on the word, every named thing in its own framing (see "The 1-to-1 method", points 5-6). Render with `scripts/render_parallel.py`.
  over 4 s**, opening mirrors ending.
- Build the scene table, run the check (MODE=check), then test pictures, a preview, and the full render.
- Write the **sound plan**: every on-screen action and its real-sounding sound (survival-story-method).
- **The two channel signatures, in EVERY Short** (owner, 10 Nov 2026; like the format benchmark's falling cyclist and its name hidden in every
  footage), whichever world the Short uses:
  1. **Ginger's cameo, once:** small, in the background, never the subject, never in the voice, not in the hook's first 2 s.
     In the lab (sf-blocky-world): one bump row (`bump crates` / `buoy` / `tank` / `hose`) or her splat. Other worlds: she runs
     in behind and bumps into something there, or splats.
  2. **The channel's name hidden on ONE real object:** in the lab it happens by itself (crates, lifebuoy, sub or dive
     cylinder). Other worlds: mark one object the way it would really be marked ("@RODIOCEAN" / "SUBSCRIBE": a stencil on a
     crate, a ship's name on a hull, a label on a can), using the prints in `assets/brand/world_prints/`. Never a corner logo,
     never two at once.
  Write both in JOURNEY.md (e.g. "Signatures: Ginger bump buoy at 6.2 s; name on crates") and pick a different gag and a
  different object from the last Short. Point both out to the owner in the stills.
- **CHECK must be clear before any full render.** Then stills (one per scene) to the owner.
- **Gate:** the owner approves the stills. Then full render, loop-seam check, preview with voice. **Gate:** the owner approves the preview.

### 6. Edit (skill **sf-edit**)
- `captions.py`, `music_pick.py` (next track in the rotation sprint -> clocks -> steps), whooshes from the render's whips, `bash edit/render.sh v1`, `format_check.py <video> short` must show **11/11**, phone copy.
- **Brand** (sf-edit step 3b, `edit/src/brand.json`): no ping at the start (owner, 12 Nov 2026), ONE proof readout when the measured number is said, the wave crash at most once (setback or a change of place). No logo or intro before the hook.
- **No-voice test** (survival-story-method): watch a muted-voice preview once; list any beat that doesn't read and fix it with the picture or a sound.
- **Gate:** the owner watches the phone copy.

### 7. Thumbnail (skill **sf-thumbnail**)
- Write 5-8 cover concepts as text and score them with **packaging-method** (cover-the-text test, text adds not repeats, one first stop + one accent colour or arrow, mid-action); run **packaging-critic** on the title + cover + first line.
- GPT-image-2.5 node in ElevenCreative: confirm the exact model id with `creative_get_model_guide`, write the prompt, build the node, price it with `estimate_only`. **The owner presses Generate.** Then `thumb_vertical.py` adds 0-3 glowing words; phone-size check.
- **Gate:** the owner picks the thumbnail. Log its credits.

### 8. Post and learn (skill **sf-posting**)
- `post_kit.py`, cover pick (A/B), `calendar_plan.py next <slug>`: one post a day, **16:00-22:00 local time** (he has been choosing 21:00).
- **Schedule through Metricool** (sf-posting Step 4): `metricool_prep.py`, then one-time Dropbox links, then one Metricool post for YouTube Shorts, Instagram Reels, TikTok and Facebook Reels, then check Metricool stored the full video and cover. **Only after the owner's explicit OK for that post** ("post it at 21:00"); only then `--publish public` for that one post (without it nothing goes out publicly by itself). No subtitles (owner: "Skip subtitles").
- `tracker.py log-post` once it has gone out; `/log-stats` at **24 h** and **7 days** (Metricool's analytics first).
- **After about 10 Shorts**, write **our viral recipe list** in `reference/OUR_VIRAL_RECIPE.md` from the top performers (what they share: hook type, length, music, thumbnail, topic), add the headline rules to `lessons.md`, and redo it whenever views drop.

## What gets written down, every stage
| Stage | JOURNEY.md (dated line, plain English) | tracker.py |
|---|---|---|
| 1 | angle, title, topic-check result | `add-episode <slug>` |
| 2 | claims confirmed, what was dropped | - |
| 3 | each panel round: score, biggest fix; "Script LOCKED: vN" | - |
| 4 | in-house takes made (voice_make.py printout), the owner's pick by ear | - (free) |
| 5 | scene count, CHECK result, stills version, loop seam numbers, render version | - |
| 6 | track used, MUSIC_IN, loudness, format check score | (music_pick records the track) |
| 7 | prompt version, price, owner's pick | `credits <slug> <amount> "thumbnail"` |
| 8 | post time per platform, 24 h and 7 d numbers | `log-post`, `log-stats` |

Every credit the owner spends gets a `credits` line, even small ones, so the Credits sheet adds up per episode.

## Money and safety (never weakened)
> - **Claude builds, the owner clicks.** Claude may build ElevenCreative boards, write prompts and price runs with `estimate_only`. Claude never runs a generation, never presses Generate, Publish or "Run from here". A settings hook enforces this; never ask to loosen it.
> - The same for every other paid service (3D generators, `generate_3d` in the Blender pack, paid APIs): no spend without the owner's OK for that exact run.
> - The voice is made in-house and free (`voice_make.py`, stage 4); ElevenLabs only if the owner asks for it again, and then he makes the takes himself.
> - Never save over an original `.blend`; ask before any download.
> - No real person's face or likeness; creators anonymous until the last line.
> - Claude schedules a post (Metricool, sf-posting Step 4) only after the owner's explicit OK for that exact post, in the chat. Never on its own initiative, never from an approval of a build or of another Short.
> - **No render before the owner approves the build in the browser** (owner, 14 Nov 2026: "From now on you NEVER rendering before I approve the build in the online broswer (local host)"). `scripts/review_server.py serve <episode> <port>` plays the edit live on localhost with a click-to-note system and an Approve button; rough drafts of only the changed 3D seconds may be shown there first (he allowed them). The final render and the final export wait for his Approve, on the page or in the chat.

## What to say to the owner
> - Plain everyday English. Short. Lead with what changed and what it means for the Short.
> - No file paths, code, commands or script names unless he asks. Say "the voice check", "the 3D world", "the music bed".
> - Explain any technical word in a few words ("loop seam: how invisible the jump from the last frame to the first is").
> - Be honest and judgemental about ideas, including his. Report critic scores as they are.
> - He often reads on his phone: each closing message must stand on its own.
> - End with **one clear question** (the gate), e.g. "Shall I lock this script?"

> - He judges the video, not still pictures: once he has said "build it", deliver a watchable cut. Offer choices as things he can see or hear.
> - Count every headline number twice before saying it.

## Picking up a half-finished episode
Run `tracker.py status` and read the episode's JOURNEY.md. Say in one line where it stands ("voice approved, 3D stills next") and continue from the next unfinished gate.
