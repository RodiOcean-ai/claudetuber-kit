# Eleven styles, one sandwich

The same 15-second explainer, "how to make a peanut-butter sandwich" (36 words, 1920x1080, 30 fps), built in 11
animation styles with Remotion (React code that renders video), plus two three.js versions of the comic and whiteboard
styles. This is the test project behind the `explainer-*` skills in the Short Factory plugin.

| ID | Style | Needs pictures? |
|---|---|---|
| S01-KineticTypography | Kinetic typography | no |
| S02-MotionGraphics | Motion graphics | no |
| S03-Screencast | Screencast | no |
| S04-Isometric | Isometric | no |
| S05-Whiteboard | Whiteboard (picture-maker drawings) | yes, included |
| S06-Comic | Comic (picture-maker panels) | yes, not included |
| S07-TwoPointFiveD | 2.5D | yes, included |
| S08-Collage | Collage | yes, not included |
| S09-CharacterStory | 2D characters with a story | no |
| S10-ThreeD | 3D animation (three.js inside Remotion) | no |
| S11-StopMotion | Stop motion | no |
| T05-WhiteboardThreeJS | Whiteboard, pen strokes worked out from 3D models | no |
| T06-ComicThreeJS | Comic, live 3D panels | no |

## Run it
1. Install Node.js 20 or newer, then in this folder run `npm install` (about 2.4 GB of packages).
2. Add your own `public/audio/voice.wav` and `public/audio/music.wav`, and the sound effects listed in `public/sfx/README.md`.
3. `npx remotion studio` opens every style in the browser.
4. The review page (every style live, one tab each; click a spot or press N for a note, C for a comment on the whole
   video, double-click a track on the timeline under the player for a note on one sound; approve a build):
   `python review/serve.py 3020`, then open http://127.0.0.1:3020. After you add your own voice and music, run
   `python review/make_timeline.py` once so the timeline shows their waveforms.
5. Render an approved style: `python tools/render.py S01` (needs FFmpeg on the PATH; it refuses a style that has no approval
   on the review page).

Or just open the whole kit in Claude Code, type **install**, and then ask Claude to "open the sandwich project".

## What is where
- `src/shared/`: the shared beat sheet (`timing.ts`, `words.json`, `phrases.json`), fonts, sound track and three.js helpers.
- `src/styles/`: one folder per style.
- `tools/`: voice timing, picture cut-outs, whiteboard tracing, sound levels, render and master.
- `review/`: the review page (the `review-page` template of the Short Factory plugin): `contract.json` (one tab per
  style) and `manifest.json` (the five steps, the words, the voice and music files) feed `make_items.py` and
  `make_timeline.py`; `serve.py` runs the page.
- `assets_work/`: the picture prompts and generator scripts (the pictures themselves are not included).
- `public/fonts/`: Google web fonts (SIL Open Font License; Permanent Marker: Apache 2.0); their licences are in
  `public/fonts/licenses/`.
