# Pictures brief: eleven-styles-sandwich (14 Nov 2026)

Project: the same 15-second "how to make a peanut-butter sandwich" video in 11 explainer styles (Remotion, 1920x1080).
Script (locked): "Take two slices of bread, then dig a knife into the peanut butter and spread it right to the edges.
Press the second slice on top and cut it corner to corner, because triangles taste better."
Five steps + payoff: (1) two slices of bread, (2) knife into the peanut-butter jar, (3) spread right to the edges,
(4) second slice pressed on top, (5) cut corner to corner (diagonal), (6) payoff: two triangle halves.

## Rules (the owner's, non-negotiable)
- Free and local only: ComfyUI on this PC (port 8188, already running) via
  `py -3.13 <your-picture-maker>/make-picture.py "prompt" <out/path/name> --size WxH --n N [--seed S] [--negative "..."]`
  (Qwen-Image 2512 + 4-step Lightning; writes name-1.png, name-2.png ...). NEVER use ComfyUI "partner" / API nodes
  (Bria, Recraft, Kling, etc.): they cost money. No ElevenLabs, no paid service of any kind.
- make-picture.py's DEFAULT negative prompt contains "cartoon, illustration, flat vector": for drawn styles (whiteboard,
  comic) pass your own `--negative` without those words.
- No real human faces anywhere (hands are fine). No readable text, letters, logos or labels in the pictures (we add all
  text in code). No radar/sonar visuals.
- CHECK EVERY PICTURE BY EYE (open the PNG with the Read tool). Reject: extra/missing fingers, warped knives, melted jars,
  text artifacts, food that doesn't look like it should (peanut butter = thick, creamy, warm tan-brown; bread = sliced
  white sandwich bread with a golden-brown crust, the classic slice shape with a domed top).
- Nothing is rendered or exported as video. Do not touch src/, review/, package.json or anything outside the folders below.
- Size names for make-picture.py: 1328x1328 (square), 1664x928 (wide), 928x1664 (tall), 1472x1104, 1104x1472.

## Where things go
- Chosen pictures: `<kit>/eleven-styles-sandwich/public/img/<style>/` with the names below.
- Everything else (all tries, rejects, scripts' scratch): `<kit>/eleven-styles-sandwich/assets_work/<style>/`.
- Reusable scripts you write (keying, tracing): `<kit>/eleven-styles-sandwich/tools/`.
- `public/img/<style>/manifest.json`: a list of {file, w, h, what, notes} (+ extra fields asked for below).
- Log: append to `<kit>/eleven-styles-sandwich/log/pictures.md`, per style: start and
  end time (`date +%H:%M`), number of generations made, number kept, what was hard. Exact numbers: they go in a video.

## Cut-outs (transparent PNGs)
Generate on a solid flat green background (add to the prompt: "isolated on a solid flat pure green background, no shadow,
nothing else in frame") and key it out with a small Python script (py -3.13 has numpy, cv2, PIL): HSV green threshold,
despill the green fringe, feather 1-2 px, keep the main component(s), trim to content with ~10 px padding, save RGBA PNG.
Check each cut-out by eye composited on BOTH a dark and a light background (save those check images in assets_work).
If green fails for an item, try a pure white background with a flood fill from the borders.

## Style 5: whiteboard -> public/img/wb/  (do this first)
Six simple line drawings: black marker on pure white, one clean uniform thick outline weight, friendly and simple, few
details, NO shading, NO hatching, NO text, object centred with white margin. 1328x1328, make 3-4 tries each, keep the best.
  - wb_bread.png: two slices of sandwich bread side by side, front view, classic slice silhouette, crust line inside the edge
  - wb_jar.png: an open jar of peanut butter (blank label, no text) with a butter knife dipped in, the lid lying beside it
  - wb_spread.png: one bread slice covered in peanut butter with a butter knife spreading it (a few swoosh lines for texture)
  - wb_stack.png: a whole sandwich, two slices stacked, at a slight 3/4 angle so the filling layer shows at the edge
  - wb_cut.png: a whole sandwich on a cutting board with a big knife slicing it diagonally corner to corner
  - wb_halves.png: two triangle sandwich halves on a round plate, slightly apart, filling visible
Then TRACE each chosen drawing into ordered centre-line pen strokes so the video can draw it stroke by stroke:
binarize, skeletonize (cv2.ximgproc is NOT available: implement Zhang-Suen thinning in numpy or similar), walk the
skeleton graph into polylines, drop bits under ~12 px, simplify (Ramer-Douglas-Peucker ~1.2 px), join strokes whose ends
nearly touch, and order them the way a person draws (big outer shapes first, then inner details, roughly top-left to
bottom-right). Measure the drawing's real line thickness (median) for the stroke width.
Write wb_<name>.strokes.json = {"w":1328,"h":1328,"strokeWidth":<px>,"strokes":[[x0,y0,x1,y1,...], ...]} (integers or 1
decimal) and a check image assets_work/wb/wb_<name>.strokes.png (the strokes drawn at that width, side by side with the
original). Look at it: the traced drawing must read the same as the original (no missing parts, no spaghetti).
Color fills (nice to have, after the rest of whiteboard is done): wb_<name>_color.png, same size, the drawing with flat soft
marker colours flood-filled into its closed areas (cv2.floodFill at seed points you pick by looking): bread #F4D79B,
crust #C98B3A, peanut butter #A8642C, metal #D9DEE3, glass #DDEFF7, plate #FFFFFF, board #D9A86C; black lines kept on top.
The drawing hand: hand_marker.png, a photo-real right hand holding a black whiteboard marker as if drawing, seen from
above at a slight angle, natural skin, wrist and a bit of forearm (sleeve fine), cut out (RGBA). 3 tries, keep the best.
In the manifest give the marker tip position in that PNG as "tip": [x, y] (px), measured by eye/zoom, accurate to ~5 px.

## Style 6: comic -> public/img/comic/
Six panels, classic American comic-book illustration: bold black ink outlines, halftone (Ben-Day) dot shading, flat vivid
colours, dynamic angles, motion/speed lines. NO text, NO speech bubbles, NO faces (hands only). Keep the look consistent
across panels (same colour palette: warm yellows, peanut-butter browns, sky-blue accents; same ink weight).
  - cm_1_bread.png (1328x1328): two slices of white sandwich bread on a wooden cutting board, top-down, kitchen counter
  - cm_2_knife.png (1328x1328): close-up, a hand plunging a butter knife into an open jar of peanut butter, low angle, action lines
  - cm_3_spread.png (1664x928): a hand spreading thick peanut butter across a slice of bread right to the edges, motion lines
  - cm_4_press.png (1328x1328): two hands pressing the top slice down onto the sandwich, squash/impact lines
  - cm_5_cut.png (1664x928): a big kitchen knife slicing a sandwich diagonally corner to corner, speed lines, dramatic angle
  - cm_6_triangles.png (1664x928): two triangle sandwich halves on a plate, hero shot, sparkles, sunburst background
3-4 tries each; keep the best; consistency between panels matters more than any single panel being perfect.

## Style 7: 2.5D (photo layers, moving camera) -> public/img/p25/
Photoreal, soft warm morning light from the top-left, one consistent high 3/4 camera angle (about 40 degrees down).
  - bg_kitchen.png (1664x928): a kitchen counter, warm wooden countertop, an EMPTY wooden cutting board in the centre front,
    softly blurred kitchen background (tiles, a plant, window light), no people, no text. 3 tries.
  - Cut-outs (same angle and light, keyed from green): c_bread.png (one slice of white sandwich bread lying flat), c_bread2.png
    (a second, slightly different slice), c_jar.png (open glass jar of creamy peanut butter, plain jar, no label),
    c_lid.png (the jar's lid lying flat), c_knife.png (clean butter knife lying flat), c_knife_pb.png (butter knife with a
    dollop of peanut butter on the blade), c_slice_pb.png (a bread slice lying flat, peanut butter spread edge to edge with
    swirl marks), c_sandwich.png (a whole peanut-butter sandwich lying flat, filling visible at the edge),
    c_halves.png (the sandwich cut diagonally into two triangles, slightly apart), fg_herb.png (a small potted herb plant,
    for a blurred foreground layer).

## Style 8: collage -> public/img/collage/
Vintage magazine cut-out look: 1960s print photographs, slightly faded colours, visible print grain/halftone.
  - kraft.png (1664x928): brown kraft paper background, slightly crumpled, even light, no text.
  - paper_white.png: a torn strip of white paper with ragged torn edges (cut-out), and tape_1.png / tape_2.png: pieces of
    beige masking tape (cut-outs).
  - Cut-outs from vintage-photo style pictures: v_bread.png (a slice of bread), v_jar.png (an open jar of peanut butter, no
    label text), v_knife.png (a butter knife), v_hand.png (a hand holding a butter knife, no face), v_halves.png (two
    triangle sandwich halves), v_plate.png (a vintage plate).
  - For every v_*.png also save v_*_border.png: the same cut-out with a ~16 px white paper border around it (dilate the
    alpha, fill white, slight irregularity like scissors) so it looks hand-cut from a magazine.

## Textures for the 3D and stop-motion styles -> public/img/tex/
1328x1328, flat even light, close-up, filling the frame, no objects, no text:
felt_cream.png (cream/beige felt fabric), felt_brown.png (peanut-butter brown felt fabric), felt_tan.png (golden tan felt),
cardboard.png (corrugated/kraft cardboard surface), wood.png (light oak cutting-board wood grain), crumb.png (macro of
white bread crumb), pb.png (macro of smooth creamy peanut butter surface with gentle swirls).

## Report back
A short summary: what is in each public/img/<style>/ folder, anything that failed or looks weak (be honest), the tip
position of the hand, and the per-style minutes and generation counts you logged.
