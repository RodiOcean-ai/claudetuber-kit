---
name: explainer-stop-motion
description: Make an explainer clip with the STOP MOTION look (faked, no real objects) in Remotion and @remotion/three - a felt-and-cardboard miniature set on a gingham tablecloth (felt bread with stitched edges, a felt peanut-butter piece, a kraft-paper jar with a hand-written label and a felt lid, a card-and-stick craft knife), 12 poses a second with a tiny hand-placed wobble in every pose, replacement pieces instead of smooth growth, a hair of light flicker and a soft painted backdrop like a close lens. Approved after 1 fix round (14 Nov 2026). Use whenever the owner says "stop motion", "claymation look", "felt", "handmade look", "paper craft", "12 fps look", or with explainer-styles for a multi-style test.
---

# Stop motion (the faked look)

Read `explainer-styles` first. Rank 11 of 11 in the ranking, but fast in code: 3 minutes to a first build, 2 owner
notes, approved after 1 fix round. Art direction from the `stop-motion-craft-style` skill: visible craft seams, real
craft materials, slight irregularity, practical light, stepped motion.

## The reusable pattern (`reference/StopMotion.tsx`)
- **Poses, not frames:** `pose = floor(frame / 2.5)` (12 poses a second at 30 fps) and every animation reads the pose's
  frame. Progress is LINEAR in poses (no smooth easing: real stop motion has none).
- **Hand-placed wobble:** each object gets a tiny random offset and twist per pose (`rand(pose * k + seed)`), the camera a
  tiny bump per pose, the light a ±2.5 % flicker per pose.
- **Replacement pieces:** the peanut butter grows in fixed sizes (0, 30, 45, 60, 72, 85, 100 %), the squash is a separate
  "squashed" pose for two poses, the flip turns in 30-degree steps.
- **Craft materials drawn on canvases:** felt = fibre strokes over a base colour, used as colour AND bump map; stitches as
  dashed lines along the slice outline drawn on the felt texture; gingham, cardboard stripes, a kraft label with a
  hand-written "P.B."; roughness 1 everywhere except the silver card blade.
- **Soft backdrop:** the painted wall and shelf are plain HTML behind the transparent 3D canvas, blurred 6 px (like a close
  lens), plus a vignette.

## Pitfalls (owner's notes)
- "The PB is inside the cutting board": the jar stood half inside the board; stand it on the cloth behind the board.
- "This doesn't look like a knife": a plain stick reads as a stick. Give it a knife silhouette: card blade with a rounded
  tip painted silver, a felt collar, a wooden handle; for the cut it stands upright and slices down along the diagonal.
- Peanut butter must reach the edges and show between the slices (felt piece 99 % of the slice).
- Keep the halves apart far enough to read as two triangles (about 0.34 units at the end).

## Numbers (14 Nov 2026)
Build 3 min (1 self-check round), 2 owner notes, 1 fix round, render 19.0 s, 17.6 MB.
