---
name: video-editing
description: Edit a YouTube video with a measured story-first editing method (from our study of a faceless channel's editing tutorial "How I Actually Edit Viral Videos", 776k views, and its 9 videos), rebuilt in Remotion - colour-coded script → asset lists, voice-over first then music straight after (cut to the beat), visuals layered per script highlight, plain text on black, sketched-then-built motion graphics (typewriter text, drawn lines, glow), eased zooms with a consistent focus point, three kinds of on-screen text with a pop animation, a mascot cut-out, screen-blend overlays (light leaks, electricity, dust), a sound pass with whoosh/riser/impact done on mute, colour grade, and "space" where a point must land - plus the measured house numbers. Use whenever the owner asks to edit, cut, add motion graphics, text pops, overlays, sound design, transitions, "edit the video", "make the edit more alive", or when a shorts-format, what-if-longs or channel-playbook video reaches its edit stage.
---

# Video editing: a story-first edit, rebuilt in Remotion

From the studied creator's editing tutorial (I02) and measured on all 9 videos (faceless-channel study of 29 Oct 2026; your own downloads in `<studies_root>/faceless-channel`, shipped notes in `${CLAUDE_PLUGIN_ROOT}/reference/creators/faceless-channel/EDITING_NOTES.md`; the measured house style is in `references/house-style.md`). He edits in Premiere Pro and After Effects; we do the same moves free in **Remotion** (a code-based video editor already installed), plus generated pictures from ElevenCreative.

**Copy the craft, never the identity:** no ginger mascot, no his yellow/black glow look as a whole, no his music tracks. Our channel's own palette, font and mascot (thumbnail-design stage 1).
**Claude builds, the owner clicks:** generated pictures and clips are priced first and the owner presses Generate. The edit itself is free.

## The two rules over everything
1. **Good editing isn't using many effects; it's using them to support what's being said.** Resist the effects tab.
2. **"People don't have shorter attention spans, they have higher standards."** Cut everything that doesn't serve the goal, but don't cut the story: leave **space** where a point, a joke or a reveal must land.

## Stage 0. Before opening the editor
- The idea and the script must already work (story-scripts). "An amazing edit can't save a boring script."
- **Watch a good film with an editor's eye** before a big edit: transitions, montages, camera angles, story beats. Most of it has never been done on YouTube; that's where originality comes from.
- **Pick ONE new technique to learn for this video** and note it in `JOURNEY.md`. 3 hours learning it now becomes 3 minutes next time. Channels that repeat the same edit forever stall.

## Stage 1. Colour-code the script (free)
Mark every sentence with one of 6 picture types, then collect everything per type before editing:
| Code | Type | Our source |
|---|---|---|
| A | **Animation / motion graphic** (flowcharts, diagrams, numbers, maps) | built in Remotion (free) |
| S | **Screen recording** (an app, a website, analytics) | recorded locally, or recreated as a mock-up in Remotion |
| F | **Footage** (real-world clips) | generated video (Seedance, priced), or licensed stock |
| I | **Image** | generated stills (gpt-image / Nano Banana, priced), moved in the edit |
| T | **Text on black** (a key line alone on screen) | Remotion (free) |
| M | **Mascot moment** (our character in a scene, a skit) | mascot cut-out over a still or a generated shot |
Write `beats.md`: sentence → code → the exact picture → how it enters and leaves.

## Stage 2. Project and timeline order
1. Remotion project at 1920×1080, **60 fps** (his choice; motion graphics look smoother). Never modify the owner's other Remotion projects.
2. **Voice-over first:** the comped, finished narration from natural-ai-voice. Its Whisper word times drive everything.
3. **Music straight after** (not at the end): it sets the vibe and lets cuts land on beats. One bed per section mood, switched on a whoosh, never mid-sentence. Level from `references/house-style.md`.
4. **Layer the pictures by the colour codes,** cutting on narration phrases or music beats.
5. **Rough cut, then watch it again:** add memes/animations where it sags, cut boring lines and unneeded shots, sometimes rewrite a line. Add space where needed.

## Stage 3. Motion graphics (free, Remotion) — `references/remotion-recipes.md`
- **Sketch first** on paper or in words: what appears, in what order, on which words. Example: boxes connected by arrows, headings blurred; zoom into box 1 and its text un-blurs.
- **Build** with shapes, text and lines; **animate** to the voice: typewriter text, lines that draw themselves (his "trim paths"), boxes that pop in, then **a glow** to make it pop.
- Simple ones can be made in Canva and exported large (zooming into a small export looks soft).

## Stage 4. Movement and focus
- **Zooms and moves:** keyframe scale and position, always **eased** (smooth curves), never linear.
- **Keep the point of focus in the same spot across cuts** (on a rule-of-thirds point or the centre), so the eye never hunts.

## Stage 5. Text: only three kinds
1. **Key-word captions:** only where something important is said, not all the way through (a word popping every second gets irritating).
2. **Centre text:** for moments captions can't carry; its own colour and glow.
3. **In-scene text:** stuck to a screen, a wall or an object in the shot.
**The pop:** scale 70 % → 110 % over 7 frames → 100 % over the next 5 frames (at 60 fps), eased; optionally a glow or a quick glitch. Save it as one reusable component.

## Stage 6. Mascot, overlays, effects
- **Mascot:** our character's head/body as a cut-out (generated, background removed) placed onto stills or stock, moved with eased keyframes. Reusable component.
- **Overlays:** videos on black, blended with "screen" so the black disappears: **light leaks for transitions** (his most-used), electricity, dust, smoke. Generated with an ElevenCreative video model on a black background, or free packs.
- **Effects he reaches for:** glow, 3D tilt (perspective transform), blur, mosaic/pixelate. Plus transition moves: slide, shake, zoom, rotate.

## Stage 7. Sound design (half of the video)
- **Mute the voice and music** and watch the picture alone; add effects where they feel right. Then unmute.
- The base three: **whoosh** (moves and transitions), **riser** (build into a reveal), **impact** (the hit). Then specific ones: clicks, keyboard, gears, camera shutters, meme sounds, a clock.
- Combine and layer effects; then **turn them down** until they never annoy.
- Sources: ElevenLabs Sound Effects (priced) or free libraries.
- Measured density and levels: `references/house-style.md`.

## Stage 7b. Music as comedy (his most-used trick, measured)
Cut the music bed to near-silence 1-3 s before or on a punchline, joke or reveal, then slam it back on the next line (5-15 clear drop-outs in a long video). Turn into the ending on 7-8 s of near-silence, then switch to a soft new bed. Details: `references/house-style.md`.

## Stage 8. Colour and finish
- A grade on each clip: exposure, contrast, saturation so generated and stock material match.
- Mix: voice -14 LUFS alone, music and effects under it by the house gap, master to about -14 LUFS for YouTube long-form, true peak -1 dB.
- Export H.264 1920×1080 60 fps, CRF 16-18, AAC 192 kbps; number every render.

## The study's 9-step edit order (from the AI-video challenge, a good checklist)
voice-over in order and pauses cut → music → clips matched to voice and music → zooms and transitions → overlays (smoke, dust, light) → sound effects on key points → colour grade → letterbox (cinematic bars, optional) → export.

## For shorts-format videos
The format benchmark's look is cleaner: no overlays, no text pops in shorts (captions only), swipes instead of light leaks. From this method take only: the colour-coded beat list, music-first timing, eased moves with a consistent focus point, the muted sound pass, and the "space" rule before reveals. For **what-if-longs**, this method's centre text and simple motion graphics (maps, counters, flowcharts) fit well.

## Reference files
- `references/house-style.md`: the measured numbers (cuts per minute, shot length, music share and switches, sound-effect density and kinds, loudness) and the visual style per section type.
- `references/remotion-recipes.md`: code patterns for the text pop, typewriter, drawn lines, glow, eased zoom with fixed focus, screen-blend overlays, swipes, parallax stills, mascot cut-out.

Source: our own analysis of public videos from Isaac (@isaacverse). Not affiliated with or endorsed by Isaac or @isaacverse.
