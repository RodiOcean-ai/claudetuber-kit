---
name: explainer-3d-animation
description: Make an explainer clip in 3D ANIMATION style with Remotion and @remotion/three (no Blender, previewable live) - a tabletop food-commercial set (marble counter, wooden board, bread with crumb and crust, a glass jar, steel knives) with physically based materials, a studio reflection map built in code, a warm key light with soft shadows, filmic tone mapping and a cinematic camera that never stops moving; slices drop, the lid flies, the knife scoops and spreads, the top slice turns over, a chef's knife slices corner to corner and the halves part to show the layers. Approved after 1 fix round (14 Nov 2026). Use whenever the owner says "3D", "3D animation", "product commercial look", "three.js", "3D in Remotion", "no Blender 3D", or with explainer-styles for a multi-style test.
---

# 3D animation: a food commercial on a tabletop, in code

Read `explainer-styles` first. Rank 10 of 11 (realistic people would be much harder; this set has none). 6 minutes to a
first build, 1 owner note, approved after 1 fix round. Because it runs in the browser, the owner reviews it live before
any render (the Blender route would need renders first, against his rule).

## The reusable pattern (`reference/ThreeD.tsx` + `explainer-styles/reference/shared/three-shapes.ts`)
- `ThreeCanvas shadows` (perspective, fov 34). The camera is a list of [frame, position, target] keys: gaps of 16 frames or
  less are whips (eased), longer gaps are slow drifts, so the camera is always moving.
- Reflections without downloads: `PMREMGenerator.fromScene(new RoomEnvironment())` as `scene.environment` (intensity 0.55),
  ACES tone mapping. Metal knives (metalness 1, roughness 0.2) and glass then look real.
- Textures drawn on canvases (crumb specks, crust, wood grain, marble veins, soft blurred peanut-butter swirls) with
  `colorSpace = SRGB`; no image files needed.
- Bread: extruded slice outline with a bevel, material 0 = crumb texture, material 1 = crust texture.
- The cut: real closed half-solids (clip the outline polygon, extrude each half), each half stacked bread / peanut butter /
  bread, a cut-face card along the cut (pushed slightly outward so the bevel does not hide it).
- The chef's knife stands upright in the vertical plane of the cut line and travels along it while going down.

## Pitfalls
- "The bread disappears into the cutting board": a spring overshoot sank the slice; clamp the height and squash instead.
- Props must stand on the counter, not inside the board (the jar went behind the board).
- Peanut butter drawn as hard arcs looks like wood: blur the swirls; it must reach the edges and show between the slices.
- A tiny dollop reads as nothing: the knife's dollop is a sphere 0.12 units, full size as soon as it leaves the jar.
- In the browser pane the 3D view can draw blank after a seek while the card is busy: seek the next frame and back. The
  render is fine (every frame waits for the canvas).

## Numbers (14 Nov 2026)
Build 6 min (2 self-check rounds), 1 owner note, 1 fix round, render 19.7 s, 15.0 MB.
