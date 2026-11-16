---
name: explainer-kinetic-typography
description: Make an explainer clip in KINETIC TYPOGRAPHY style with Remotion (pure code, no pictures) - every word lands on its spoken word and acts out its meaning (a word splits, slides in like a blade, stretches, flies to the edges, squashes, gets cut), word groups sit on one big page and a camera whips from group to group with motion blur, and the ending pulls back so the whole page becomes the hero object (a slice of bread cut corner to corner). Approved by the owner first time (14 Nov 2026, 0 notes). Use whenever the owner says "kinetic typography", "moving words", "text animation", "words only video", "typography style", "make the words act", or with explainer-styles for a multi-style test.
---

# Kinetic typography: the words ARE the picture

Read `explainer-styles` first (voice, beat sheet, review page, render). This is the easiest style (rank 1 of 11): pure code,
no pictures, about 7 minutes to a first build, approved with no notes.

## The look
Cream background, three-colour palette taken from the subject (here bread gold, peanut-butter brown, near-black ink) plus
one accent (channel blue) for guides. Heavy rounded sans (Rubik 900) for the words that matter, an italic serif
(Instrument Serif) for the small linking words ("then", "of", "into the").

## The reusable pattern (`reference/Kinetic.tsx`)
1. **One big page, many word groups.** Each phrase is a group (flex rows) placed at page coordinates with a small tilt.
   Lay the groups out in a shape that pays off at the end (here 2 columns x 3 rows = roughly square, so the whole page fits
   inside a bread slice).
2. **The camera** is one transform on the page: `translate(960,540) scale(s) rotate(-r) translate(-x,-y)`. Keys per group;
   gaps of 26 frames or less are whips (bezier 0.75,0,0.25,1), longer gaps are slow drifts (always moving). Interpolate
   the scale on a log scale so zooms feel even. Blur the page by the camera's speed during whips (max 7 px).
3. **Words land 2 frames before they are heard** (`at(k) - 2`) with a spring pop; small words rise from a mask.
4. **Words act their meaning** (one helper, many kinds): SLICES splits into two halves, KNIFE slides in like a blade with a
   gleam, PEANUT BUTTER letters wobble like goo, SPREAD stretches (scaleX 0.3 -> 1.25), EDGES letter-spacing flies out,
   PRESS squashes, TOP drops on top, CUT is cut along a diagonal, TRIANGLES letters spin in inside a drawn triangle.
5. **The payoff:** pull back to the whole page, clip it to the hero shape (SVG path as CSS `clip-path: path()`), draw the
   crust outline on, then cut corner to corner: the page drawn twice, each clipped to one side of the diagonal, moving
   apart along the diagonal's normal, with a peanut-butter line along the cut edge.

## Sound
A soft swipe on every camera whip, a small hit per acting word (pop, zip for the blade, smack for DIG, thud for PRESS, whip
for CUT, marker stroke for the dashed corner-to-corner line), whoosh on the pull-back.

## Pitfalls
- Measure word widths in the browser before setting a fixed width (SPREAD at 250 px overlapped "it"): stretch from the
  centre inside a fixed-width box instead.
- A drift key copied from another group's position makes the camera slide to the wrong place: write every key's x/y.
- Words placed on a diagonal need room: give the diagonal box its own size and check the first and last words fit.
- Two cut directions in one video read as a mistake: the payoff cut must not run through the payoff words.

## Numbers (14 Nov 2026, 15 s, 1920x1080)
Build 7 min (2 self-check rounds), 0 owner notes, render 38.4 s, 5.4 MB.
