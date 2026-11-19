# Free Claude Code video kit (from the RodiOcean channel)

A skill for every animation style in the video, the base they share, the sandwich project, and the whole Shorts kit.
Free under the MIT licence.

**Start here:** open this folder in Claude Code and type **`/start-claudetube`**. A friendly guide takes you through the 7 steps of the video (install, a 2-minute demo, your niche, your style and brand, your first video, your voice, then preview, upload and a weekly rhythm), one step at a time, can learn from your own channel's link, and remembers where you stopped.

## What is in it
- **`short-factory/`**: a Claude Code plugin (skills, critics and commands Claude can use):
  - **One skill per explainer style**: kinetic typography, motion graphics, screencast, isometric, whiteboard, comic,
    2.5D, collage, 2D characters, 3D animation and stop motion (`explainer-*`), plus **`explainer-styles`**, the base
    they share (one script, one voice, one beat sheet, the review page, rendering).
  - **The Shorts kit**: `/study-channel` (measure a channel's top videos and write down what works), `/make-short`
    (subject, facts, script with a critic panel, free local voice, a blocky 3D world in Blender, the Remotion edit,
    thumbnail, posting plan, with a yes/no from you after every step), `/critic`, `/post-plan`, `/log-stats`, `/status`.
  - **Method guides and critics** from our own studies of public channels, each named after what it does (for example
    `shorts-format`, `stakes-ladder-method`, `curiosity-gap-method`, `packaging-method`, `shorts-format-critic`,
    `story-critic`), with the measured numbers behind them. Each ends with one source line naming the channel studied.
    Independent analysis of public videos; not affiliated with or endorsed by any creator or channel named in the kit.
  - **Channel basics for beginners** (plain English, each with YouTube's own help pages as sources):
    - `yt-niche`: find your niche (what you know + a passion, your edge, a free demand check, a 3-5 video test).
    - `yt-branding`: name and @handle, logo, banner, colours, fonts, mascot and one voice, kept in one brand sheet.
    - `yt-titles`: titles that get clicked without lying (patterns that work, max loading, scoring options, A/B tests).
    - `yt-thumbnails`: thumbnails a stranger gets in one glance (one hero, 0-3 words, phone check, no AI-slop look).
- **`eleven-styles-sandwich/`**: the sandwich project, the same 15-second "how to make a peanut-butter sandwich"
  explainer in 11 styles, as Remotion code.
- **The review page** (`short-factory/templates/review-page/` + the `review-page` skill): your video plays live in the
  browser on your own PC, nothing rendered. Click a spot (or press N) to pin a note at that exact moment, press C for a
  comment on the whole video, double-click a track on the editor-style timeline (picture, clips, voice with every word,
  music, sound effects) to note one sound. Claude answers under each note, and nothing is rendered until you press
  Approve. The notes list follows the moment that is playing. The sandwich project already uses it. Ask Claude:
  **"set up the review page"**.

## Install
**Shortest way:** paste this into Claude Code:

`Install https://github.com/RodiOcean-ai/claudetuber-kit`

Claude asks where to put the kit (it suggests your Documents folder), downloads it and sets it up. When it's done, open
that folder in Claude Code and type **/start-claudetube**. (For Claude: follow "Installing from the link" at the top of
`INSTALL.md`.)

**Or by hand:**
1. Download this folder (green **Code** button, then **Download ZIP**) and unzip it.
2. Open the folder in **Claude Code**.
3. Type **install**.

Claude checks what your PC is missing (Python, Node.js, FFmpeg, Blender), asks before every step, and sets up the
plugin. Made on Windows 11; on a Mac or Linux tell Claude your system, most steps are the same.

## What you need
- Claude Code (needs a paid Claude plan). Everything else in the kit is free.
- For the 3D world: Blender 4.2 or newer. For the edit: Node.js 20 or newer.
- Remotion is free for individuals and small companies; bigger companies need a Remotion company licence.

## Not included, and how to get it
| Not included | Why | How to get it |
|---|---|---|
| Music and sound effects | paid or licence-limited | Your own, the YouTube Audio Library, Openverse or Freesound (CC0). For real instruments, run `short-factory/scripts/get_instruments.py` (free CC0 recordings, about 740 MB); Claude can then compose music with them. |
| Voice samples | the author's channel voice | Record two short samples of your own voice (see `short-factory/assets/voice/README.md`). |
| Pictures for the comic and collage styles of the sandwich project | 60 MB | Make them with a local picture maker from the prompt scripts in `eleven-styles-sandwich/assets_work/`, or use the three.js comic, which needs no pictures. |
| The RodiOcean brand (logo, name prints, sounds) | the author's channel identity | Make your own with the `yt-branding` skill (it writes your brand sheet), see `short-factory/assets/brand/README.md`. |
| Downloaded videos, frames and transcripts of other creators | not ours to share | `/study-channel` downloads fresh ones on your own PC for study, and deletes the videos afterwards. |
| The author's tracker, settings and notes | personal | The install makes an empty tracker and your own settings file. |

## You stay in charge
- Claude never presses **Generate** in a paid tool and never spends money: it builds and prices, you decide.
- Claude posts nothing without your OK for that exact post.
- Use what you learn from studying a channel; never re-upload anyone's footage.

## Licence
MIT (see `LICENSE`): free to use, change and share, also in paid work, as long as the copyright line stays in your copy.
The web fonts in the sandwich project keep their own licences (`eleven-styles-sandwich/public/fonts/licenses/`).
