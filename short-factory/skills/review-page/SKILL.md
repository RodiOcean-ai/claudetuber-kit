---
name: review-page
description: Set up and run the review page in any Remotion project - a page on this PC where the video plays live in the browser (nothing is rendered), one tab per thing to review; the person clicks a spot or presses N to pin a note at that moment, presses C for a comment on the whole video, double-clicks a track on the editor-style timeline under the player (picture, clips, voice with every word, music, sound effects, notes) to note one sound, reads Claude's answer under each note and approves each tab; the notes list scrolls by itself and follows the chapter that is playing. Then the note loop - read the notes, fix, reply, new build - and never render before the person approves. Use whenever the person says "the review page", "set up the review page", "I want to leave notes on the video", "show me the video in the browser", "timeline with the voice", "read my notes", "answer my notes", "approve", "review before rendering", or before rendering any Remotion video.
---

# The review page

A page on this PC (for example http://127.0.0.1:3030) that plays the video live with the Remotion Player. Nothing is
rendered. The person pins notes on the picture, comments on the whole video, notes a single sound on the timeline, reads
your answers and approves. You read the notes, fix, answer, and render only what was approved.

Talk to the person in plain words: "the review page", "your notes", "approve". No file names or commands unless they ask.

The template is `${CLAUDE_PLUGIN_ROOT}/templates/review-page/` (its `README.md` explains the data contract). A working
example with one tab per style is the kit's sandwich project (`eleven-styles-sandwich/review/`).

## Set it up in a project (about 10 minutes)
1. **Check the project.** It is a Remotion project with `src/` and its packages installed (`node_modules`). The page
   needs `@remotion/player` at the same version as `remotion`: if it is missing, ask, then run
   `npx remotion add @remotion/player`. Python 3.9 or newer.
2. **Copy** the template's `review/` folder into the project (`<project>/review/`). If the project already has a
   `review/` folder, ask first and keep its `notes.json` and `builds.json`.
3. **Fill the contract**: copy `review/contract.example.json` to `review/contract.json`. Read `src/Root.tsx`: one item
   per composition the person will review, in a sensible order (the whole video, then each chapter, then covers).
   `id` = the composition id; `module` + `export` = where its component lives; `frames` = its `durationInFrames`;
   `width`/`height` when not the default; `props` = its input props if it needs any. A chapter of a longer video gets
   `"chapter": "<id>"` instead of `frames`.
4. **The manifest (optional, worth it when there is a voice)**: `review/manifest.json` from
   `review/manifest.example.json`. Fill it from what the project already has: chapters (start and length in frames),
   the word times (point at the project's own words file if there is one: `"words": "src/data/words.json"`), the voice and
   music files in `public/` with the frame where each starts, music sections. Name it in the contract (`"manifest"`).
   No word times and no chapters? Leave the manifest out: the timeline still shows the sounds and clips it finds.
5. **Build the data**: `python review/make_items.py` and `python review/make_timeline.py`. Fix anything they report
   (a wrong module or export, a chapter id that is not in the manifest, a sound file that is not there).
6. **Mark what is ready**: `python review/serve.py build <id> "Build 1" --change "what is in it" --standin "what is a
   placeholder"` for each tab the person should look at. Tabs without a build show "not built yet" and no approve button.
7. **Start it** in the background: `python review/serve.py 3030` (if the port is taken it says so: use the next one).
   For the app's browser pane add `.claude/launch.json` with
   `{"version": "0.0.1", "configurations": [{"name": "review", "runtimeExecutable": "python", "runtimeArgs": ["review/serve.py", "3030"], "port": 3030}]}`.
8. **Check it yourself before you send the link**: the page opens without console errors, the picture draws (open
   `/?clean#<id>`, run `window.reviewPlayer.seekTo(<frame>)`, take a screenshot), the timeline shows the words.
9. **Tell the person** the address and the four moves: click a spot (or N) for a note on the picture, C for a comment
   on the whole video, double-click a track for a note on that sound, the green button to approve.

## The note loop
1. **Read**: `python review/serve.py notes` (all tabs) or `notes <id>`. The running server also prints each new note as
   it arrives. A note has its time, the spot (x and y as a share of the width and height), or a track plus the exact
   thing on it (for example `"knife" in "then dig a knife into the peanut butter"`). "WHOLE VIDEO" = a comment on the tab.
2. **Fix** it in the project's code. Look at the result yourself (`?clean`, seek, screenshot) before you answer.
3. **New build**: `python review/serve.py build <id> "Build 2" --change "..."`. The new label means an earlier approval
   no longer counts for it.
4. **Answer** under every note: `python review/serve.py reply <id> <n> "what I changed" done` (n = the note's number on
   the page; whole-video comments are numbered first). Leave out `done` when you need the person's answer, and ask it in
   the reply.
5. The page shows "Claude changed the videos: reload" by itself. Tell the person in one line what changed.

After the voice, the chapters or the music change: run `make_timeline.py` again (and `make_items.py` if lengths changed).

## Never render before approval
Render a tab only when its CURRENT build label is approved on the page (`notes` lists the `APPROVED` lines; they are in
`review/notes.json` under `approvals`, with the tab id and build label) or the person approved that exact build in the
chat. Render only what changed. Open notes on an approved build: ask before rendering.

## When something is off
- The page says it "could not be built": read the message; usually a wrong `module` or `export` in the contract. Fix,
  run `make_items.py`, reload. "esbuild was not found" = run `npm install` in the project.
- A blank or broken picture: read the browser console; a file missing from `public/` shows as a failed request.
- 3D compositions sometimes draw a blank frame after a seek while the graphics card is busy: seek one frame on and back.
- The sound-effects track fills in as the video plays (the page reads the sounds from the composition itself).
- Files the page writes in `review/`: `notes.json`, `builds.json`, `sounds.json`, `review.js`, `_bundle/`. Keep
  `notes.json` and `builds.json` (they are the person's notes and approvals); the rest can be rebuilt.

Older pages in this kit: `scripts/review_server.py` (the Shorts edit of a short-factory episode) and the first version in
the explainer-styles skill. This page does everything they do, plus the timeline, whole-video comments and track notes.
