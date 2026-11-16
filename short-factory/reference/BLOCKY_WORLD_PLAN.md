# Blocky world: plan to make it fast to build and render (5 Nov 2026)

Goal: any new Short in the blocky style is written as a simple scene table, built automatically from ready-made banks
(characters, places, moves, faces, camera shots) and rendered in under 30 minutes, without dropping below the look test
(lookdev/blocky_hero, version 2, approved look direction).

Today's numbers: the test scene builds and renders 8 full-size pictures in about 17 seconds (about 1.5 s a picture).
A 30-second Short is 900 pictures, so about 25 minutes. Most of the time saved has to come from the building, not the rendering.

## 1. Character bank (the cast)
- One builder: a character is a short recipe (name, skin, top, trousers, shoes, head shape, accessory, face set).
- Accessory library: headphones (our hero), hats (bucket, cap, beanie, crown), hair blocks, glasses, hood, backpack, tie, apron.
- The hero changes with every episode (owner, 5 Nov 2026): restyled to match the channel being reviewed, with its colours
  and one signature item, but never the creator's face or likeness. The side characters (mayor, teacher, kid, inspector)
  keep fixed recipes.
- Every character gets an automatic character sheet (front, side, back, 3 faces), so the owner approves a person once.
- Saved as a Blender asset library as well, so a character can be dragged into a scene by hand if needed.

## 2. Face bank
- 12 expressions (calm, happy, laughing, shocked, scared, angry, sad, crying, smug, confused, sleepy, determined).
- 4 mouth shapes for talking (closed, half, wide, O), switched automatically from the voice's word times.
- Blinks added automatically every 2-4 seconds; eyes can look left or right.

## 3. Place bank (sets)
- Modular town pieces: 5 house types, shop, school, road, fence, trees, lamp posts, park bench, car.
- Indoor rooms: classroom, bedroom, kitchen, office, shop counter.
- Each place is a recipe ("street, 3 houses, evening light"), so a new location takes one line.
- Three lighting presets: day, golden hour, night (with street lamps and glowing windows).

## 4. Moves bank (animation)
- Ready moves that work on every character: stand (with breathing), walk, run, wave, point, talk gestures, shrug,
  jump in shock, fall over, cry, sit, turn around, run away.
- Moves blend into each other automatically, so there are no jumps between them.
- Feet stay on the ground (automatic check).

## 5. Camera bank
- Shot presets: wide, two-shot, close-up, over the shoulder, low hero angle, slow push-in, whip to the next place.
- Uses the same holds-and-whips camera as our Shorts, timed to the voice.

## 6. The scene table (how a Short is written)
One line per beat: time or word, place, who, move, face, camera shot. Example:
| word | place | who | move | face | shot |
|---|---|---|---|---|---|
| "In this town" | street-day | hero | walk | calm | wide |
| "if you lie" | street-day | mayor | point | angry | close-up |
The builder turns the table into the 3D scene; no hand-building per Short.

## 7. Faster, same quality
- Preview first: a half-size, low-quality render of the whole Short in about 3-5 minutes for the owner to approve the
  timing; the full-quality render only once, after approval.
- Switch off what this flat style doesn't need (ray tracing, heavy shadows) after an A/B check that the look holds.
- Re-render only the changed shots (the partial-render trick we used on the chess episode).
- Automatic checks before any full render: nothing passes through anything, faces turned towards the camera, feet on the ground.

## 8. Make it permanent
- A new skill, sf-blocky-world, explaining the banks, the scene table, the checks and the render steps.
- Lessons from the look test go into lessons.md (owner: the head must match the can shape; adult proportions, not kids).

## Progress
- 5 Nov 2026, step 1 done: templates/blender/blocky (faces_bank.py, blocky_kit.py, cast.json, cast_sheets.py, compose_sheets.py); sheets in lookdev/blocky_cast.
- 5 Nov 2026, step 2 done: moves.py (12 moves, 0.25 s blends, feet pinned, feet check); 10 s test in lookdev/blocky_moves.
  Measured: 300 frames at full size with motion blur in about 2 minutes (0.4 s a picture), so a 30 s Short renders in about 6 minutes.

- 5 Nov 2026, step 3 done: places.py (street with 5 house types, shop, school, lamps, benches, cars; classroom, bedroom,
  kitchen, office, shop inside; each place returns spots and ready camera framings) and light presets day / golden / night.
  9 pictures render in about 35 seconds; sheet in lookdev/blocky_places.

- 5 Nov 2026, step 4 done: scene.py reads a scene table (lookdev/blocky_scene/test_scene.md) and builds places, cast,
  moves, faces, lip flaps and the camera bank (wide, medium, close, two_shot, ots, low, push_in; 0.45 s flights).
  Checks: feet, characters overlapping, framed faces in the picture and not turned away. 15 s: preview about 1 minute,
  full quality about 3 minutes. Known issue: a flight between two places crosses empty grass (fix: fly through a door).
- 5 Nov 2026, door flight fixed (owner: yes): a change of place now flies into the building's street door (school for the
  classroom, shop, a house for the other rooms); the cut happens while the door fills the picture, then an identical door
  swings open into the room (leaving a room is the reverse). The cut sits between two frames, outside the motion blur, so
  nothing smears. Rooms got a floor apron in front, so no grass shows at the edges. Full 15 s render: 3 m 25 s, checks clear.

- 5 Nov 2026, step 5 done: speed A/B (lookdev/blocky_speed): 24 samples look the same as 48 and are 13% faster (now the
  default); switching off ray tracing flattens the floors, so it stays on. Re-render only changed shots with SHOTS=3,5
  (shot 3 of the test, 94 frames: 46 s). The hero can be restyled per episode from the table ('hero:' line). Leaving rooms
  through the door tested (classroom -> street -> kitchen -> bedroom), all hand-overs match. Written up as the
  sf-blocky-world skill.
- 5 Nov 2026: owner watched test scene v2 with the door flight: "Looks good". The blocky world plan is complete.

## Order of work (each step ends with pictures for the owner)
1. Character builder and the face bank (12 faces, 4 mouths, blinks), plus character sheets for the hero and 3 side characters.
2. Moves bank, shown as a 10-second moving test with talking and blinking.
3. Place bank and lighting presets, shown as one picture per place.
4. Scene table, camera bank, preview render and the checks, shown as a 15-second test scene built only from a table.
5. Speed tuning (A/B of quality settings) and the skill write-up.

Everything above is free: no paid tools, no downloads.
- 5 Nov 2026, mystery hero (owner request): the hero can hide as a shadow figure with a glowing '?' face until a 'reveal' row,
  then pops out of a ring of sparks (lookdev/blocky_mystery). Also: single framings now film three-quarter on, a BLOCKED check,
  and the touching check compares body parts instead of whole-body boxes.
- 5 Nov 2026: owner approved the mystery hero and the reveal ("Looks good").
- 5 Nov 2026: more cast (grandpa, grandma, scientist, guard, chef, boss, a fan crowd), animals (dog, cat, rabbit, pigeon) and Pip, our running gag with the signature `splat` fall; test lookdev/blocky_cast2 (splat_v3, CHECKS all clear). Waiting for the owner's OK.
- 5 Nov 2026: the owner chose a ginger cat as the running gag: Ginger (red collar, gold bell), the cat that never lands on its feet; test ginger_v3 (CHECKS all clear). Pip stays as an ordinary character. Waiting for the owner's OK.
- 6 Nov 2026: owner approved Ginger and the fall as the running gag ("Yes, keep Ginger").
