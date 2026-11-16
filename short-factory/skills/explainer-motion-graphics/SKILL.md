---
name: explainer-motion-graphics
description: Make an explainer clip in MOTION GRAPHICS style with Remotion (flat vector shapes, no pictures) on the channel's clean explainer-board look - white dotted paper, ink #0B2540, one blue accent, Inter + JetBrains Mono; a step title with a highlighter sweep, step chips that fill as you go, a rolling counter, a coverage meter that rolls to 100 %, a dashed corner-to-corner cut line and a star-rating card for the payoff. Approved first time (14 Nov 2026, 0 notes). Use whenever the owner says "motion graphics", "shapes and icons", "explainer board look", "the templates we have" for a how-to, "chart style", "infographic animation", or with explainer-styles for a multi-style test.
---

# Motion graphics: flat shapes on the explainer board

Read `explainer-styles` first. Rank 2 of 11; 4 minutes to a first build, approved with no notes.

## The look (from the saved explainer boards, "clean ocean" version)
White paper with 1.5 px dots every 40 px, ink #0B2540, mono eyebrow line in uppercase, 76 px Inter title with a
highlighter swept under it (`linear-gradient(178deg, transparent 52%, #CFF3FF 52% 93%, transparent 93%)` growing in width),
soft cards (1.5 px #C9E6F5 border, 22 px radius, soft shadow), one accent colour per idea.

## The reusable pattern (`reference/MotionGraphics.tsx`)
- Objects are small SVG drawings in a 300 x 300 box (bread slice path with a domed top, jar with a level that drops, knife
  with a dollop) placed by one transform each; positions per step are mixed with eased progress values so every step
  re-composes the frame (slices move apart when the jar comes in, then the sandwich moves to the centre for the cut).
- The spread is a clip circle that grows on the slice; the coverage card counts the same progress to 100 % and turns green.
- The second slice lifts, turns over (scaleX from cos(pi * t)), lands with a squash; then the sandwich shows its layers
  (peanut-butter band peeking out).
- The cut: draw the sandwich twice clipped to the two triangles, part them along the diagonal's normal, draw the
  peanut-butter line along the cut edge (clipped to the slice).
- Step chips at the bottom: grey -> blue (current, lifted) -> ink with a tick (done).
- The camera breathes (a slow sine zoom of 2 %) plus a small push on every step.

## Pitfalls
- A lifted slice arcing over the frame can cover the title: keep the arc below the title line.
- Empty rating stars must stay visible (draw the grey star first, then the filled star scaled on top).
- A knife cutting "corner to corner" must lie along the cut line, tip first, not across it.

## Numbers (14 Nov 2026)
Build 4 min (1 self-check round), 0 owner notes, render 16.9 s, 4.5 MB.
