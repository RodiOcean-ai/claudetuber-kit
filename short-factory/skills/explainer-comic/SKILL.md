---
name: explainer-comic
description: Make an explainer clip in COMIC BOOK style with Remotion - one comic page of six panels made on the free local picture maker in one ink-and-halftone look (hands only, no faces, no lettering in the pictures), read by a camera that whips panel to panel, yellow narration boxes typed word by word with the voice, a big sound word on every action (FLOP! SHLUK! SWOOSH! SMOOSH! SHHNK! YUM!), a cut panel built in code so the cut really runs corner to corner, a triangle-halves payoff on a sunburst and a full-page pull-back with a stamp. Approved after 1 fix round (14 Nov 2026). Also the THREE.JS WAY with no picture maker at all: every panel a live 3D scene in a comic look (flat toon colours, black ink outlines, halftone dots in the shadows) on one 3D canvas, each panel frozen on its own moment; approved first time (14 Nov 2026). Use whenever the owner says "comic", "comic book style", "panels", "halftone", "speech bubble style", "sound words like POW", or with explainer-styles for a multi-style test.
---

# Comic: one page, read panel by panel

Read `explainer-styles` first. Rank 6 of 11. Art direction from the `comic-book-style` skill. 15 minutes to a first
build plus 7 minutes of pictures (40 tries, 6 kept); 1 owner note, fixed with 4 more pictures (1 kept).

## The pictures
- One style line in every prompt: bold black ink outlines, halftone dot shading, flat vivid colours, warm yellows and
  peanut-butter browns with sky-blue accents; NO text, NO speech bubbles, NO faces (hands only). Consistency between
  panels matters more than one perfect panel.
- The picture maker draws a "corner to corner" cut straight across or as a cross, and a "triangle halves" picture that
  does not read as triangles. Fix (owner's note: "It doesn't cut corner to corner and it's not triangle end results"):
  make ONE whole sandwich seen from straight above, cut it out (GrabCut), and build the cut and the halves in code.

## The reusable pattern (`reference/Comic.tsx`)
- Panels are absolutely placed on a page (gutters, slanted edges with `clip-path`), each picture `object-fit: cover`
  with a slow push; a halftone dot layer multiplied on top of every panel.
- The camera fits each panel (zoom = min(1920/w, 1080/h)), whips between panels (bezier 0.8,0,0.2,1, motion blur), and
  is clamped so it never looks past the page edge.
- Narration boxes show the panel's words as the voice says them (each word appears at its frame); "..." when a sentence
  carries over from the panel before.
- Sound words: Bangers font, thick black stroke (`-webkit-text-stroke` + `paint-order: stroke fill`), hard offset shadow,
  a spring pop and a short shake.
- The cut panel: the top-down picture, a white-and-black slash with speed lines drawn corner to corner, then the
  cut-out drawn twice (each clipped to one triangle) moving apart along the cut's normal, a dark copy underneath as the
  shadow in the gap, a peanut-butter line along each cut edge. The payoff panel: the two triangles on a rotating sunburst.
- Ending: pull back to the whole page and stamp the payoff line on it.

## Pitfalls
- A wide page and tall panels: the camera must clamp to the page or it shows the dark table around the page.
- The model draws thin frames around pictures: crop them before use.

## The three.js way: no picture maker (`reference/Comic3D.tsx`, approved first build, 14 Nov 2026)
Owner asked "can we use three.js instead of ComfyUI?" and approved this with no notes. Use it when there is no picture
maker or graphics card to spare: no pictures, no failed tries, runs on almost any PC, and the cut is real geometry.
- The look (`reference/three-toon.ts`): a toon material with 3 flat light bands (a 3-pixel ramp texture, nearest filter)
  and comic halftone dots where the light is low (the toon shader patched: a 45-degree screen-space dot grid, dot size
  from the light level); black ink outlines as an "inverted hull" (the same shape with welded corners and smooth
  normals, drawn back-side only and pushed out a fixed number of pixels in clip space); a `flat` canvas (no tone
  mapping); PCF shadows on a toon floor become dotted shadows.
- One canvas for the whole page: a ThreeCanvas the size of the page (dpr 1.5) inside the page camera; `useFrame(..., 1)`
  draws every panel the page camera can see: a stencil mask of the panel shape (slanted panels clip exactly; needs
  `gl={{ stencil: true }}` and stencil settings on every material), viewport + scissor on the panel, depth clear, pose
  the world for that panel's moment, render with that panel's own 3D camera. The payoff panel clears to see-through so
  the CSS sunburst shows behind the 3D triangles.
- Each panel freezes on its own moment (local time = frame clamped to the panel's step), so the pulled-back page at the
  end reads as a real comic strip. Same page, narration boxes, sound words, slash and stamp as the picture version; the
  slash runs between the sandwich's corners projected through the cut panel's own camera.
- The shapes: `reference/three-sandwichGeo.ts` (slice, peanut butter, halves cut corner to corner, both knives, sharp
  edges) plus the outline helpers in `explainer-styles/reference/shared/three-shapes.ts`.
- Pitfalls: see-through glass breaks the ink hull (the back of the hull shows through): make the jar opaque (glass
  colour above, peanut butter below, from a 2-colour texture), with a separate back-side inner wall and a rim ring. A
  knife pointing away from the camera reads as a stick standing in the bread: turn it side-on (blade flat on the
  bread, tip in, handle raised to the side). Tip the payoff triangles back about 30 degrees with the cut towards the
  camera, or the layers do not show. On the review page, changing only the address hash keeps the old code: reload.

## Numbers (14 Nov 2026)
Build 15 min + 7 min pictures (40 tries, 6 kept), 1 owner note, 1 fix round (7 min, 4 tries, 1 kept), render 25.9 s,
69.3 MB (halftone detail makes big files; fine for a master).
Three.js way: built together with the three.js whiteboard test in about 30 minutes (the cartoon look and the 3D
sandwich are shared), 0 pictures, 0 owner notes, approved first build; render: see the render log.
