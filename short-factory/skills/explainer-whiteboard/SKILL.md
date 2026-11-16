---
name: explainer-whiteboard
description: Make an explainer clip in WHITEBOARD style with Remotion - marker line drawings made on the free local picture maker, traced into ordered centre-line pen strokes and drawn stroke by stroke by a real-looking cut-out hand holding a marker, coloured in with a marker sweep, labelled in blue marker handwriting, with the camera travelling along one big board and an ending that pulls back to the whole recipe board with hand-drawn arrows and a red circle. Approved first time (14 Nov 2026, 0 notes). Also the THREE.JS WAY with no picture maker at all: the pen strokes worked out from 3D models (outlines and sharp edges as the camera sees them, hidden lines removed), colours rendered from the same models, and a 3D cartoon hand holding a marker; approved first time (14 Nov 2026). Use whenever the owner says "whiteboard", "whiteboard animation", "drawing hand", "doodle video", "being drawn", "sketch explainer", or with explainer-styles for a multi-style test.
---

# Whiteboard: the hand draws it, stroke by stroke

Read `explainer-styles` first. Rank 5 of 11. The code took 3 minutes; the work is the drawings (21 minutes: 84 drawing
tries + 6 hand tries, 7 kept). Approved with no notes.

## The pictures
- Prompt: black marker line drawing on pure white, one clean outline weight, friendly and simple, no shading, no text,
  object centred. Pass your own negative prompt (the default one forbids "illustration").
- The model coloured food in and added frames and lettuce: 4 prompt rounds were needed ("colouring-book page" removes
  colour but adds texture; straight-from-above for the cut).
- Trace each kept drawing into strokes (`explainer-styles/reference/tools/wb_trace.py`): binarize, thin to centre lines,
  walk the skeleton into polylines, drop bits under 12 px, simplify, join near ends, order big outer shapes first. Keep
  each stroke's own measured width (`widths`): one width for all merges close thin lines.
- Colour versions by flood-filling closed areas at picked seed points (`wb_fill.py`).
- The hand: a photo-real hand holding a marker, from above, cut out; record the marker tip pixel.

## The reusable pattern (`reference/Whiteboard.tsx`)
- One path per drawing = strokes in order + pen-up travel between them (so the hand never teleports); each stroke is a
  polyline revealed with `strokeDashoffset`; the pen position is the point at the drawn length.
- The hand image is placed by its marker tip on the pen point; between drawings it glides from the last to the next point.
- The colour picture sweeps in with a gradient mask; `mix-blend-mode: multiply` so its white disappears into the board.
- Labels are written left to right with a clip; the hand follows the label's writing line.
- Camera along a snake of six cells, then a pull-back to the whole board, arrows drawn on, a red ring on the payoff.
- A marker squeak about every half second while drawing; a page swish on each camera move.

## Pitfalls
- The hand picture ends at the wrist/sleeve: extend the sleeve with a polygon past the frame edge, or it looks cut off.
- Colour pictures with white backgrounds show as white boxes on an off-white board: use multiply.

## The three.js way: no picture maker (`reference/Whiteboard3D.tsx`, approved first build, 14 Nov 2026)
Owner asked "can we use three.js instead of ComfyUI?" and approved this. No pictures, no 90 tries, any camera angle, and
the drawings always match each other; everything is made in the browser when the video opens (about a second).
- Each drawing is a small three.js scene (the shapes from `reference/three-sandwichGeo.ts`) with its
  own camera, auto-framed so the models fill 84 % of the drawing square (`setViewOffset` on the projected bounding box).
- Pen strokes (`reference/three-lineart.ts`): (1) a depth picture of the scene (each triangle rasterised in code at 2x,
  keeping 1/distance), (2) candidate edges: outlines (one face towards the camera, the other away), sharp edges (over
  35 degrees) and open borders, plus detail lines that lie on surfaces (inner crust line, crumb holes, peanut-butter
  swirls, glass shine), (3) each edge sampled every 1.25 px and kept only where nothing nearer covers it, (4) the
  pieces joined into long strokes (ends within 1.3 px, turns under 68 degrees), simplified, given a small hand wobble
  (none at the ends) and ordered object by object, outline before details, nearest stroke next. Output = the same
  stroke format as the traced drawings, so the drawing hand code is unchanged.
- Colours: the same scenes rendered once by an off-screen three.js renderer in flat toon marker colours
  (`reference/three-toon.ts`), kept as pictures, swept in under the lines with multiply.
- The hand: a cartoon hand (capsule fingers wrapped round a white marker with a blue cap, thumb in front) and a flat
  sleeve, rendered once in the toon-and-ink look; the marker tip pixel comes from the projection. The SVG sleeve band
  starts where the 3D sleeve leaves the picture (so the two drop shadows do not stack into a stripe).
- The corner-to-corner line: the sandwich's real corners projected through the drawing's camera.
- Pitfalls: a closed outline (start = end) has no line to measure from, and the line simplifier threw the whole loop
  away (every top outline vanished): measure from the start point instead. The cut face of an extruded half is crust
  coloured: lay a crumb / peanut-butter / crumb plane on it for the colour picture only. Two halves seen from the side
  hide each other: look along the cut and turn each half so its layers face the camera.

## Numbers (14 Nov 2026)
Build 3 min code + 21 min pictures (90 tries, 7 kept), 0 owner notes, render 18.0 s, 13.4 MB.
Three.js way: built together with the three.js comic test in about 30 minutes, 0 pictures, 0 owner notes, approved;
render: see the render log.
