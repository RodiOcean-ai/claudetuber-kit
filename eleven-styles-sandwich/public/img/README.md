# Pictures

Included: `wb/` (whiteboard drawings, colours, the marker hand and the traced pen strokes) and `p25top/` (top-down
pictures for the 2.5D style), all made on a local picture maker, plus the small `.json` data files.

Not included (size): `comic/` (8 comic panels, about 25 MB) and `collage/` (22 cut-outs, about 35 MB). Make your own with
the prompt scripts in `assets_work/` (`comic/gen*.sh`, `collage/gen1.sh`, `gen_top.py`, `gen_rest.py`) and a local
picture maker (set `MAKE_PICTURE` or edit the `MP=` line), then save the chosen ones here with the names the code uses
(see `src/styles/s06_comic/Comic.tsx`, `src/styles/s08_collage/Collage.tsx` and `comic/manifest.json`).
Or use the three.js versions of the comic and whiteboard styles (`T06-ComicThreeJS`, `T05-WhiteboardThreeJS`): they need
no pictures at all.
