# Camera movement: Zack's top Shorts vs ours (measured 13 Nov 2026)

Tool: short-factory/scripts/camera_motion.py (tracks ~200 background points per frame and fits one shift/zoom/turn: the camera's move).
Data: camera_motion_benchmark.json (his 10 top Shorts S01-S10 + "Why Your Brain Focuses On Negative Things"), camera_motion_ours.json (our 10 finished Shorts).

| Median | Zack (11) | Ours (10) |
|---|---|---|
| Camera moving | 95 % of the time | 78 % |
| Longest still moment | 0.2 s | 0.84 s |
| Slow moves, sideways | 13 % of the picture width a second | 5 % |
| Slow moves, zoom | 6 % a second | 3.4 % |

- Zack's range: moving 78-99 %, longest still 0.03-0.93 s, sideways 5-23 %/s, zoom 3-15 %/s. His biggest Short (stitches) is one continuous move.
- Ours: chess 97 % moving, longest still 0.03 s, zoom 6.6 %/s (closest to Zack, and our most-watched; one example, not proof). Boards Shorts (pause, thumbnail rules) 36 % moving; toast held still 2.2 s.
- Why ours was slow: in scene.py every framing except push_in only creeps 5 % of the way toward its subject over the whole hold.
- Limits: "fast" frames include fast action (a falling cat), not only flights; one tracker; counts depend on the 2 %/s still threshold.

Targets for every Short from 13 Nov 2026: moving 90 %+, longest still 0.3 s or less, slow moves 10-18 % of the width a second, push-ins 4-9 % a second, a different move type each framing.


## Built and tested (13 Nov 2026)
scene.py now gives every framing its own steady move (push, pull, swing, crane, slide; tested on the scene before use). Same scene (squirrel Short, lab half, 17.7 s, chess look), old camera vs new: moving 88 % -> 99 %, longest still 0.87 s -> none, sideways 3 % -> 10 % of the width a second, zoom 3 % -> 5 % a second. Render time unchanged (531 frames in 33 min, 4 workers). Clips: <episodes_root>/rober-streak/blender/chess_a (old) and chess_a_newcam (new).
