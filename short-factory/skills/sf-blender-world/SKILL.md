---
name: sf-blender-world
description: The older one-world Blender 3D toy look for a short-factory Short (since 10 Nov 2026 the default world is the underwater lab in sf-blocky-world; use this only when the owner asks for the toy look) - the episode's world.py template with the sf_world helpers, a bright toy look, stations along one line, camera holds joined by whips timed to the voice's word times, no scene over 4 seconds, an opening that mirrors the ending so the Short loops, real physics baked to keys, an optional cartoon outline, faceless toy figures, the CHECK overlap pass before every full render, test stills to the owner, the full render, the loop-seam check and the whip list for the edit; plus guardrails for the EL4CTEO blender-* skills. Use whenever the owner says "build the 3D", "make the world", "Blender scene", "render the short", "test stills", "fix the thing going through the brain", "add physics", "outline on/off", "the loop", or when sf-pipeline reaches stage 5.
---

# The one-world 3D method

One continuous 3D world, one camera. The camera **holds** on a station (a small set that shows one phrase), then **whips** fast to the next station, timed to the voice. It is our free answer to the format benchmark's "no hard cuts, the camera always flies" look, and it beat stitched AI clips on both earlier episodes.

**Blocky town look instead?** (can-head people, street and rooms, a scene table): use skill **sf-blocky-world**.

Plain English to the owner ("the 3D world", "test pictures", "the overlap check"), no paths or code, one question at the end. Rules from `${CLAUDE_PLUGIN_ROOT}/reference/lessons.md` (section 3D) always apply.

**Run tools as:** `"<python>" -I -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/blender_tools.py" ...` (`<python>` and the Blender path from `config.json`).

## Inputs
- The approved voice and its word times (`voice/` in the episode; made in sf-pipeline stage 4).
- `script_LOCKED.txt`, `facts.md`, the subject's `SECRET_SAUCE.md` (what must be shown faithfully).
- The episode's `blender/world.py` and `common.py`, scaffolded by `new_episode.py` from the plugin template. `world.py` imports the shared helpers from `sf_world`. Read the template's top comment before editing. The parts you edit are `CUES` (word times: `T.at('but')`), the `SET`, the shot table `SHOTS` (start, end, camera from/to, look from/to, lift of the whip into the hold) and the check list `CHECKS` (pairs that must never touch). Helpers in `sf_world`: `make_bottle`, `flip`, `figure` (faceless toy, `eyes=True` only for our generic viewer), `pop`, `arc`, `wobble`, `bake_physics`, `add_outline`, `camera_rig`, `finish`. Switches: `CHECK=1`, `STILLS=...`, `OUTLINE=1`, `FRAME_START/FRAME_END`. A full worked example is `reference/creators/light-study/world_example.py`.

## Step 1. Scene plan (free) -> `scene_plan.md`
| # | Time (from word times) | Words | Picture (3D, toy-like, no real likeness) | Viewer should feel |
|---|---|---|---|---|
- **A new picture every 2-4 s; no scene longer than 4 s; no still image held.**
- One picture per phrase, shown literally (the format benchmark: when the voice says "bullet", you see a bullet).
- **Every new picture must carry the words.** Never add a cut, whip or push-in only to look busy: fast cutting that covers a weak story loses viewers (lesson from a former lead editor of a top channel). If a scene feels slow, fix the words or the picture, not the cut count.
- **Fill the "viewer should feel" column** for every scene (curious, worried, surprised, "no way"). A scene with no feeling is a scene to cut or merge.
- **Hide the series Easter egg:** the same tiny water bottle mid-flip somewhere in the world, visible for at least one hold but never in the hook's focal point and never covering the subject. Note its scene and spot in the plan.
- **Show the real thing faithfully** (the first episode's record clip: its 8 real shots, not 8 made-up ones), and make "impressive" tricks look impressive (a lone cone landing was not).
- **Opening mirrors ending:** plan the last scene to return to the first picture (the bottle mid-flip on frame one lands back on the same table at the end).
- Something moves on frame one; the subject is alone and readable at phone size.
- **Gate:** the owner OKs the scene plan (one table, one line per scene).

## Step 2. Build the world
- **Bright toy look by default:** pale-blue sky gradient, soft daylight sun, saturated but clean colours, one subject per station on a clean empty set.
- **Stations along one line** (along x), each a small set for one scene. The camera travels between them; nothing is ever cut.
- **Camera:** one hold per scene with a slow drift or push; a fast whip (eased, a few frames, motion blur) into the next hold. Whip times come from the **word times** so each whip lands as the new phrase starts.
- **People are faceless toy figures:** black silhouettes from behind or simple toys; never a real person's face or likeness, children above all. Names or colours light up only at the reveal.
- **On-screen devices** from the subject's secret sauce (counters, game boards, badges) are 3D objects in the world, never flat overlays.
- **Real physics** for bounces, falls and showers: rigid bodies simulated, then **baked to keys** so every render is identical (skill **blender-simulation**). Landings get a rocking settle.
- **Cartoon outline** is an option (inverted hull, invisible to shadows), approved for our first episode. Offer an A/B still if the owner hasn't chosen for this series.
- Brand, if any, lives on one prop inside the scene, never a corner logo.

## Step 3. CHECK before anything is rendered in full
- `blender_tools.py check <world.py>`: the overlap pass. List every pair that must never touch in the template's check list (thrown objects vs heads/brains, viewers vs phones, figures vs props).
- **CHECK must say "clear" for every pair** before a full render. It caught the bottle-through-brain (18 frames) and viewer-through-phone (109 frames) problems on the first episode, v2.

## Step 4. Test stills to the owner
- `blender_tools.py stills <world.py> <frame,frame,...>`: one frame from the middle of each scene, as a contact sheet.
- Look at it yourself first: subject readable at phone size? anything clipping, floating, black? text readable?
- **Gate:** the owner approves the stills (send the sheet, one line per scene).

## Step 5. Full render and loop
- `blender_tools.py render <world.py> <version> [--outline]`. Number every render (v1, v2, ...); keep them all.
- `blender_tools.py seam <frames_dir>`: last vs first frame difference. **It must be no bigger than a normal frame step** (first episode, v5: 8.11 vs 8.34). If not, fix the ending pose, not the edit.
- `blender_tools.py whips <render_log>`: writes `edit/src/swishes.json`, the 5 biggest whips, for the whooshes in the edit.
- Make a quick preview with the voice for the owner. **Gate:** the owner approves the preview, or lists changes (then back to step 2, CHECK again, new version number).

## JOURNEY.md lines (dated)
Scene count and longest scene; CHECK result per pair; stills version sent; render version, frames and length; seam number vs normal step; what the owner asked to change.

## Guardrails for the EL4CTEO blender-* skills
We use the audited pack (blender-core, blender-simulation, blender-stylized-npr, blender-lighting-lookdev, blender-rendering and others) for help, with these standing rules:
- **Never save over an original `.blend`.** Work from `world.py` (the world is rebuilt from code every run); if a `.blend` is saved, give it a new versioned name.
- **No `generate_3d` (or any paid 3D generator) without the owner's OK for that exact run**, after showing the price.
- **Ask before any download** (models, textures, HDRIs, add-ons): name, source and size.
- Read a bundled script before running it the first time.
- The live Blender connection (MCP) is for looking and small tests; the real build is the episode's `world.py`, run headless, so it can be re-rendered any time.

## Common fixes
| Problem | Fix |
|---|---|
| Something passes through something | move or raise it, re-time the throw, back the object off; CHECK again |
| A scene feels static | add a slow push and one moving object; never hold a still |
| Seam jumps | match the last camera pose and object states to frame one |
| Whip lands late on a word | re-read the word times; Whisper can be up to 0.6 s early |
| Thin or unreadable detail at phone size | make it bigger and simpler; one subject per station |
