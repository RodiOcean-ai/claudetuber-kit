---
name: explainer-collage
description: Make an explainer clip in COLLAGE style with Remotion - vintage magazine photos (made on the free local picture maker, seen from straight above) cut out with a hand-cut white paper border on crumpled kraft paper, moving in jerky paper-animation steps (12 a second with a small wobble), ransom-note headlines glued on torn paper strips, masking tape, a vintage hand whose knife really goes into the jar, real peanut butter appearing in torn-paper steps, scissors cutting exactly corner to corner along a dashed line, and the two triangles pasted on a vintage plate with star stickers. Approved after 1 fix round (14 Nov 2026). Use whenever the owner says "collage", "cut-out style", "magazine cut-outs", "ransom note letters", "paper cut-out animation", "scrapbook style", or with explainer-styles for a multi-style test.
---

# Collage: magazine cut-outs on kraft paper

Read `explainer-styles` first. Rank 8 of 11. First build together with 2.5D (about 21 minutes, 28 tries, 9 kept);
3 owner notes, fixed in one round with top-down pictures (9 tries, 4 used), approved.

## The pictures
- Prompt start: "Vintage 1960s magazine advertisement print photograph, slightly faded warm colours, visible print grain
  and fine halftone dots, old printed paper look, seen from directly above (flat lay)". Isolated on green, cut out with
  `explainer-styles/reference/tools/grab_cut.py`; then `paper_border.py` gives each cut-out a hand-cut white border.
- Kraft paper background, torn white paper strips and masking tape pieces (green screen, plain key).
- A hand holding a knife (side view is fine in a collage): cut out by skin and steel colours; record the knife tip pixel.
- Use TOP-DOWN slices and a top-down whole sandwich (owner's note: "not corner to corner" when the slice was at an angle).

## The reusable pattern (`reference/Collage.tsx`)
- Everything moves in poses: `f = floor(frame / 2.5) * 2.5`, linear progress, a small random offset and twist per pose.
- Ransom-note headline per step: every letter its own font, paper colour and tilt, on a torn-edge strip (polygon clip)
  that slaps on (scale 1.12 for two poses) and tears away upward at the next step. Leave a clear gap between words.
- The hand is placed by its knife tip and turned about it. **Into the jar** (owner's note "the knife doesn't go into the
  PB"): draw the hand ABOVE the jar and draw the jar's front again over the hand (`clip-path: inset(36% 0 0 0)`) while it
  digs, so the blade disappears below the peanut-butter surface.
- **Real peanut butter** (owner's note "the PB doesn't look like real PB"): the peanut-butter area cut out of a spread-slice
  photo, shown through a torn-paper polygon that grows in replacement sizes (0, 30, 45, 60, 75, 88, 100 %); the dollop on
  the knife is a torn piece of the same photo.
- **The cut:** the dashed "cut here" line and the scissors run between the top-down sandwich's TRUE corners (the opaque
  pixels with the smallest and largest x + y); then the sandwich is shown twice, clipped to the two triangles, moving
  apart along the cut's normal, with a peanut-butter line along each cut edge; the plate slides in under them.
- Sounds: paper rustle for every headline, slice lands, page swish, smack in the jar, rustle while spreading, thud on the
  press, tape zip, scissors, sparkle at the end.

## Numbers (14 Nov 2026)
First build about 21 minutes with 2.5D (28 tries, 9 kept); 3 owner notes; 1 fix round (9 tries, 4 used); render: see the
render log.
