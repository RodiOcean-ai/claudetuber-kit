# The review page (template for any Remotion project)

A page on this PC (http://127.0.0.1:3030) where the video plays live in the browser with the Remotion Player. Nothing is
rendered. The person watching:
- clicks a spot on the picture (or presses **N**) to pin a note at that exact moment;
- presses **C** for a comment on the whole video (one tab);
- double-clicks a track on the editor-style timeline under the player (Picture, Clips, Voice with every word, Music,
  Sound effects, Notes) to note one exact sound;
- reads Claude's answer under each note, and presses **Approve** per tab when it is right.

The notes list scrolls on its own and follows the moment (and the chapter) that is playing. Each tab shows a dot with its
open notes and turns green when approved. `?clean` after the address shows only the video (for Claude's own checks).

The `review-page` skill tells Claude how to set it up. In short: copy the `review/` folder into the project, fill in
`review/contract.json`, run the two builder scripts, start `review/serve.py`.

## What the project provides (the data contract)
1. **`review/contract.json`, required: the list of things to review**, one tab each. For every tab: `id`, `name`,
   the file and export of its component (`module`, `export`, optional `props`), and its length (`frames`, or
   `"total"`, or a `chapter` from the manifest). Optional per tab: its own `width`/`height` (a cover, an upright Short),
   `mark` (the text in its circle), `start` (where it sits on the timeline), `timeline: false`, `music: false`.
   Example: `review/contract.example.json`; every field is listed at the top of `review/make_items.py`.
2. **A manifest, optional: what the timeline shows.** Chapters (id, title, style, start, frames), the spoken words with
   their frames (inline or the path of the project's own words file), the voice and music files in `public/` with the
   frame where each starts, music sections (name, tempo, chords, instruments) and sound files to hide. Example:
   `review/manifest.example.json`; every field is listed at the top of `review/make_timeline.py`. Without a manifest
   the timeline still shows the clips, sound effects, voice and music the page finds in the compositions as they play.

## The files
| File | What it does |
|---|---|
| `review/make_items.py` | contract -> `items.gen.tsx` (what the page plays) + `items.json` (the tab ids) |
| `review/make_timeline.py` | manifest -> `timeline.json` (chapters, sentences, words, music, waveforms) |
| `review/serve.py` | the local server (127.0.0.1 only) and Claude's commands: `notes`, `reply`, `build` |
| `review/ReviewApp.tsx`, `Timeline.tsx`, `index.html` | the page (bundled with the project's own esbuild) |
| written while in use | `notes.json` (notes and approvals), `builds.json` (each tab's build), `sounds.json`, `review.js` |

Needs: the project's `npm install` done (Remotion brings esbuild and the Player; add `@remotion/player` at the same version
as `remotion` if it is missing), Python 3.9 or newer. FFmpeg and numpy are used when present, not required.
