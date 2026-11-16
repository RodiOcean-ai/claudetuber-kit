---
name: explainer-2d-character
description: Make an explainer clip in 2D CHARACTER ANIMATION style with a little story, in Remotion (flat SVG, no pictures) - a cartoon puppet built from parts (a penguin chef: body that leans, squashes and hops, belly, apron, eyes that look and blink and squint, a beak that chomps, a chef's hat, two flippers that reach for things along keyed paths) acting every step behind a kitchen counter, props that are held, twisted, tossed and landed, a sound for every action, and a payoff where the character bites the result and melts with happiness. Approved after 2 fix rounds (14 Nov 2026). Use whenever the owner says "2D character", "cartoon character", "mascot explains it", "a character with a story", "puppet animation", "flat cartoon", or with explainer-styles for a multi-style test.
---

# 2D character with a story: a puppet acts it out

Read `explainer-styles` first. Rank 9 of 11 ("without direction Claude falls back to stick figures"). 8 minutes to a first
build, 2 owner notes, approved after 2 fix rounds. Art direction from `cartoon-style` and `vector-style`: silhouette first,
bold flat colours, detail in shapes, a dark outline on props.

## The reusable pattern (`reference/CharacterStory.tsx`)
- **A puppet, not a drawing:** the body is one group (translate, lean rotation, squash with volume kept: scale(1/sqrt(s), s)),
  the face reads the look direction (pupils move inside the eye whites), blinks on fixed frames, squints while
  concentrating, closes into happy arcs at the payoff; the beak opens to chomp.
- **Flippers (arms) are computed every frame** from the shoulder (rotated with the body) to a tip point that follows a
  keyed path ([frame, [x, y]] with easing). Everything held is drawn at the tip, so the arm and the prop never separate.
- **Props change owner:** each prop has a state per frame range (on the counter, held, flying, landed). A lid twists while
  held, then flies on an arc and bounces; slices lie flattened on the board (cartoon perspective = scaleY 0.42) and
  unflatten when lifted; the flip turns the slice by scaling its height through 0.
- **A small story:** hop of excitement at the start, a focused squint while spreading, a big wind-up and slash for the cut,
  then he takes a bite (bite marks = circles in a mask), crumbs fly, eyes close happily, hearts float up.
- A real sound for each action: bag rustle, slice lands, lid zip and pop, smack in the jar, paper rustle for spreading,
  whoosh and thud for the press, a whip for the slash, crunches for the bite.

## Pitfalls (owner's notes and self-checks)
- An arm crossing the face to reach the far side reads badly: give each job to the flipper on that side.
- "He lifts the knife through the jar": a held knife must go straight down into the jar and straight up out of it, and the
  part inside the jar is hidden with a clip above the jar's mouth.
- "He spreads it with the handle": the flipper holds the HANDLE, so the hand stays to the side of the slice and the BLADE
  (with the peanut butter on its tip) lies across the bread.
- Lines drawn along a cut must be clipped to the bread, or they poke out past the crust.

## Numbers (14 Nov 2026)
Build 8 min (2 self-check rounds), 2 owner notes, 2 fix rounds, render 13.0 s, 3.1 MB.
