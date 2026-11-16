---
name: sf-edit
description: The Remotion edit for a short-factory Short - word-timed 1-3-word captions corrected against the locked script, the next music bed in the rotation (sprint -> clocks -> steps) placed so its final hit lands on the last word and frame one sits on a beat, soft whooshes on the biggest whips, two-pass mastering to -12 LUFS / -1 dB true peak, the 11-point format check against the format benchmark's measured ranges, a phone copy for the owner and the silent-pause check. Use whenever the owner says "edit the short", "put it together", "add captions", "add music", "which music", "render the final", "make a phone copy", "check it against the format", "the pause isn't silent", or when sf-pipeline reaches stage 6.
---

# The edit: picture, captions, music, whooshes, master, check

The edit folder is made by `new_episode.py` (Remotion template with the shared `node_modules` link). 1080x1920, 30 fps, one composition. Never touch the owner's other Remotion projects.

Plain English to the owner ("captions", "the music bed", "the loudness", "the format check"), no paths or code, one question at the end.

**Run tools as:** `"<python>" -I -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py" ...` with `<python>`, `ffmpeg_dir` and the fonts from `config.json`.

## Inputs
Approved voice (`voice/`), `script_LOCKED.txt`, the approved render frames or video from the 3D stage (**sf-blocky-world**, the lab, by default; **sf-blender-world** if the owner chose the toy look), and `edit/src/swishes.json` from `blender_tools.py whips`.

## Step 1. Captions
- `captions.py <episode_dir>` writes:
  - `edit/src/words.json`: Whisper word times, with each word corrected against `script_LOCKED.txt` (Whisper hears "turn" for "turned");
  - `edit/src/captions.json`: phrase starts of **1-3 words**, numbers kept whole ("13 BILLION" is one caption).
- Read the caption list yourself: every phrase must split cleanly; no caption covers the subject's face or the platform's bottom and right-side button zones.
- Style (the format benchmark, re-measured 12 Nov 2026 on its model Short): white, thin black outline, **small and low**: 62 px, 2-3 words, centred at about y 1400 (in the episode's `captions.tsx`: top 1300, font 62, stroke 5), word-by-word with the voice. No other words on screen.

## Step 2. Music (the rotation)
- Three beds rotate in order: **sprint -> clocks -> steps -> sprint ...** The tracker knows which was used last (`tracker.py music-next` shows the next one).
- `music_pick.py <episode_dir>` picks the next track, computes **MUSIC_IN** so the track's **final hit lands on the last word** and **frame one sits on a beat**, writes `edit/src/music.json`, copies the wav into the edit and records the choice in the tracker.
- Use `--track sprint|clocks|steps` only if the owner asks for a specific bed (say that it breaks the rotation).
- Levels: **voice 16-19 LU above the music** (the format benchmark's model Short: 19; set the music volume to about 0.085), music under the voice the whole time, no gaps.

## Step 3. Whooshes
- 2-5 soft whooshes on the **biggest whips** from `swishes.json` (top 5 by size). Fewer is better; the format benchmark keeps them sparse.
- Place them with the voice and music muted, then set them low enough never to annoy (the video-editing sound pass).
- One impact or pop only if the story has a real physical hit.

- **Sounds from Openverse** (owner asked, 12 Nov 2026) only when our own library lacks one: CC0 / public domain (preferred) or CC BY (credit line in the description); never BY-SA, NC or ND; check the licence on the sound's own page; show him the candidates before any download; log licence and credit in the post kit.

## Step 3b. Brand (RodiOcean "Sonar" look; `${CLAUDE_PLUGIN_ROOT}/assets/brand/BRAND.md`, owner's picks 10 Nov 2026)

> **Shared kit:** the RodiOcean brand files (logo, name prints, sounds, backgrounds, letter font) are not included. Put your own files in `assets/brand/` with the same names (see its README), or leave the brand off. Your own brand sheet `assets/brand/BRAND.md` (made with the **yt-branding** skill) wins: when it exists, use its colours, fonts and text style instead of the house look below.

Set it in `edit/src/brand.json`; the template's `brand.tsx` does the rest (it sits above the picture and BELOW the captions, so the words stay readable). Older episodes made before 10 Nov have no brand layer: copy `brand.tsx`, `brand.json` and `public/brand/` from the template only if the owner asks.
- **No ping at the start, ever** (owner, 12 Nov 2026: "remove the ping at the start, don't do it anymore also in future video"). The template has no ping any more.
- `"readouts": [{"at": <second the voice says the number>, "value": "x42", "label": "NORMAL"}]`: **one proof readout per Short**, only for a number we measured ourselves ("x42 NORMAL", "15 of 20 HITS"); it brings the echo ping. If it covers the subject, move it with `"y"` (pixels from the top, default 330).
- `"waves": [<second>]`: the sea transition: a band of water sweeps the picture **from right to left at one constant speed, 0.4 s in all** (owner, 12 Nov 2026: the old wave crash was too slow and slowed down in the middle); the picture is fully covered at that second, so put the change of picture there. Use it **at most once** in a Short: at the setback, or where the story jumps to a new place. Never on every cut.
- **Yellow means "measured":** nothing else in the edit (captions, labels) is lemon yellow.
- The format check allows 0-12 sound effects a minute and counts the echo and the wave: with the brand on, keep whooshes to 2-3.

## Step 4. Render and master
- Inside the episode folder: `bash edit/render.sh v1` (then v2, v3 ...; keep every version). It renders, then masters in two passes to **-12 LUFS, true peak -1 dB**.
- No title card, no end card, no "subscribe". The video ends on the last word.

## Step 5. Format check: 11/11
- `format_check.py <video.mp4> short`: 11 checks against the format benchmark's measured ranges (length, words, speaking speed, voice on frame one, long pauses, cuts, loudness, voice over music, music share, sound effects, captions).
- **Fix every NO** with what we already have (re-time, trim, re-level) before anything that costs money. Explain any false alarm honestly. The first episode's edit v1 scored 11 of 11.

## Step 6. Silent-pause check
A pause before a punchline must be **truly silent**. Whisper's word times can be up to 0.6 s early, so check against the waveform:
- `"<ffmpeg_dir>/ffmpeg" -i <voice.wav> -af silencedetect=noise=-40dB:d=0.15 -f null -` lists the real silences.
- Compare with the gaps in `words.json`. If a planned pause has breath, music swell or a whoosh in it, move or trim it. No pause over 0.5 s anywhere.

## Step 7. Phone copy
- `"<ffmpeg_dir>/ffmpeg" -y -i out/<final>.mp4 -c:v libx264 -crf 26 -preset medium -c:a aac -b:a 160k out/<slug>_phone_vN.mp4`
- Send the phone copy to the owner (small enough to watch on his phone). **Gate:** the owner approves, or lists changes.
- When approved, copy the master into `post/` as the FINAL file.

## JOURNEY.md lines (dated)
Edit version; track used and MUSIC_IN; whoosh count; brand (ping, readout value and second, wave second or none); length, loudness, true peak, voice-over-music gap; format check score; silent-pause result; the owner's verdict.

## What to tell the owner
"Edit v1 is ready: 32 seconds, music bed 'steps' with the last hit on 'bottles', 5 whooshes, passes all 11 format checks. Phone copy attached. Is it good to go, or what should change?"
