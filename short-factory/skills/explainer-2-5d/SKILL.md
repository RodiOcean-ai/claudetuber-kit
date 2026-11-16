---
name: explainer-2-5d
description: Make an explainer clip in 2.5D style with Remotion - flat photo cut-outs (made on the free local picture maker) stacked at different heights in CSS 3D space and filmed by a moving camera so higher things slide over lower things (parallax), with soft shadows that move with each layer's height; best as a TOP VIEW over a table (the owner's pick after the side view failed): slices drop onto a board, a lid lifts off an open jar, a knife dips into the real peanut butter, the spread appears under the blade, the top slice flips over in 3D, a knife cuts exactly corner to corner and the halves part, with blurred foreground leaves drifting past. Approved after 1 fix round (14 Nov 2026). Use whenever the owner says "2.5D", "parallax", "photo layers", "depth from flat pictures", "top view", "flat lay animation", or with explainer-styles for a multi-style test.
---

# 2.5D: flat photos, real depth

Read `explainer-styles` first. Rank 7 of 11. First build (side view) took about 21 minutes with the collage and got 4 notes;
the TOP VIEW rebuild fixed all four in one round and was approved.

## Why the side view failed (owner's notes on Build 1)
"The bread doesn't look like it is on the cut board, maybe try to do a top view look"; "not sure what's happening with the
knife and the PB"; "spread with the edge of the knife, not the handle"; "this is not corner to corner". A front/3-quarter
view needs every cut-out to match the background's perspective exactly; generated pictures never do, and a diagonal cut of
a slice seen at an angle never reads as corner to corner. From straight above everything lies flat in one plane, so the
pictures line up and the diagonal is the real diagonal.

## The pictures (one turn on the picture maker, 27 tries, 10 used)
Prompt start: "Photoreal food photograph shot from directly above (flat lay, top-down, 90 degrees), soft warm morning
light from the top left". Board on a counter (empty), two bread slices, a slice spread with peanut butter, a whole
sandwich, an open jar of peanut butter, its lid, a clean butter knife and one with a dollop (horizontal, tip LEFT), basil
on white. Cut out with `explainer-styles/reference/tools/grab_cut.py` (`--metal` for the knives; for a knife a band-limited
GrabCut around the knife works when the green has a light patch); basil by colour saturation.
The peanut butter: cut ONLY the peanut-butter area out of the spread slice (colour mask, eroded away from the crust) and
lay it over the plain slice, so the spread is real peanut butter.

## The reusable pattern (`reference/TwoPointFiveD.tsx`)
- `perspective: 1600` on the frame; one world div at the centre with `translate3d(0,0,push) rotateZ(turn) translate3d(-x,-y,0)`
  (camera keys [frame, x, y, push, turn]); every layer is `translate3d(x, y, z)` with z = height above the table
  (table -900, objects -880, held knife -760, foreground leaves +360).
- `Layer`: the picture at its height plus its shadow on the table: the same picture `brightness(0) blur()` offset to the
  lower right by its height (light from the top left), lighter and softer the higher it is.
- Dropping = falling from a big height (closer to the camera, so bigger) with the overshoot turned into a squash.
- The knife is placed by its TIP (`knifeAt`: rotate the tip offset, subtract it from the target).
- Into the jar: lower the knife to the jar's rim height and draw the jar's peanut-butter circle again just above it
  (clip-path circle), so the blade disappears into the peanut butter.
- Spreading: the blade lies on the bread (tip left, handle off the slice) and sweeps 6 passes; the peanut-butter layer is
  revealed by an SVG mask of rounded bands along every pass the blade made, softened with a Gaussian blur.
- The flip: `rotateY(180deg)` while the slice is lifted (it grows as it rises).
- The cut: measure the sandwich picture's true corners (the opaque pixels with the smallest and largest x + y), slide the
  knife tip first along that line with a thin cut line behind it, then show the picture twice clipped to the two
  triangles (polygons through the corners, extended), moving apart along the line's normal, with a peanut-butter line
  along each cut edge.

## Numbers (14 Nov 2026)
Build 1: about 21 minutes with the collage (33 tries, 11 kept); 4 owner notes; fix round 1 (top-view rebuild, 27 tries,
10 used) in the 22-minute 2.5D + collage round; render: see the render log.
