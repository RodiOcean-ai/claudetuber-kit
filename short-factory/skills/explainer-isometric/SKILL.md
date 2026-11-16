---
name: explainer-isometric
description: Make an explainer clip in ISOMETRIC style with Remotion and @remotion/three (no Blender) - a small diorama on a counter block seen from a locked true-isometric orthographic camera, flat colours with a key light from the upper left so top / left / right faces read as three tones, soft shadows, objects that drop in, flip, get spread and cut corner to corner into real closed half-solids, and callout labels with leader lines that track the 3D anchors. Approved after 1 fix round (14 Nov 2026). Use whenever the owner says "isometric", "iso view", "diorama", "game-like 3D", "the 45 degree look", or with explainer-styles for a multi-style test.
---

# Isometric: a locked iso camera on a tiny diorama

Read `explainer-styles` first. Rank 4 of 11; 5 minutes to a first build, 2 owner notes, approved after 1 fix round.
Art direction from the `isometric-style` skill: lock the angle for the whole set, readable silhouettes, strong top faces.

## The reusable pattern (`reference/Isometric.tsx` + `explainer-styles/reference/shared/three-shapes.ts`)
- `ThreeCanvas orthographic flat shadows`; the camera sits at target + (10, 10, 10) looking at the target (true iso); only
  the target and the zoom move (keys [frame, zoom, x, y, z]). Never rotate an iso camera.
- `proj()` turns a 3D point into screen pixels for the same camera, so HTML callout labels with leader lines stay glued
  to 3D anchors while the camera pans and zooms.
- Bread = the slice outline (`sliceShape`) extruded with a bevel and two materials (faces = crumb, sides = crust).
- The cut: clip the outline polygon with the diagonal (`clipHalf`), extrude each half as its own closed solid, stack
  bread / peanut butter / bread per half, and lay a textured "cut face" card along the cut (`cutSegment`) so the layers show.
- Lambert materials with flat colours, ambient + hemisphere + one shadow-casting directional light.

## Pitfalls (owner's notes)
- "The bread disappears": a spring that overshoots sinks the slice into the board for a few frames. Clamp the drop at 1
  and turn the overshoot into a vertical squash.
- "The jar is sealed": an open jar needs a rim (torus) and an open glass tube, not a solid disc on top.
- The first light setup was too dark for flat colours: ambient about 1.0, key about 2.4.
- In the browser pane the 3D view can draw blank after a seek while the card is busy: seek the next frame and back.

## Numbers (14 Nov 2026)
Build 5 min (1 self-check round), 2 owner notes, 1 fix round, render 16.4 s, 5.3 MB.
