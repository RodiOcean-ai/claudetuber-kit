---
name: sf-blocky-world
description: Build and render a Short in our blocky 3D world from a simple scene table - a ready cast (the hero restyled per episode, plus mayor, teacher, kid, inspector, mom, grandpa, grandma, scientist, guard, chef, boss, fans for a crowd, and animals - dog, cat, rabbit, pigeon), Ginger our running-gag ginger cat with the signature 'splat' fall (the cat that never lands on its feet), 12 face expressions, lip flaps and blinks, 12 moves that blend, a street and five rooms with day / golden / night light, a camera bank (wide, medium, close, two-shot, over the shoulder, low, push-in) joined by quick flights, a fly-through-the-door change of place, a mystery hero (shadow with a glowing question mark) until a sparkling reveal, automatic checks (feet, overlaps, faces in the picture), a 1-minute preview and a full render, and re-rendering only the shots that changed. Use whenever the owner says "blocky", "blocky world", "the underwater lab", "build the 3D", "make the world" (the lab is the default world for every Short since 10 Nov 2026), "the town", "the mayor / teacher / kid / inspector", "scene table", "build the scene from the table", "restyle the hero for this channel", "Ginger", "the ginger cat", "the running gag", "Ginger bumps into something", "bump and fall", "the lab crates / lifebuoy / submarine", "logo on things in the lab", "signature move", "the fall", "Pip", "add a dog / cat / pigeon", "animals", "a crowd", "mystery hero", "the question-mark figure", "reveal the hero", "preview the blocky scene", "re-render shot 3", or when sf-pipeline stage 5 uses the blocky look instead of the one-world toy look.
---

# The blocky world: a Short from a table

A whole scene is one markdown table, one line per action. The builder makes the places, the people, their moves, faces and
mouths, the camera and the checks, then renders. Nothing is placed by hand. Built 5 Nov 2026 (plan in
`${CLAUDE_PLUGIN_ROOT}/reference/BLOCKY_WORLD_PLAN.md`); the look is the owner-approved can-head, adult-proportion blocky style.

Plain English to the owner ("the scene table", "the preview", "the checks", "the door flight"), no paths or code, one question
at the end. Rules from `${CLAUDE_PLUGIN_ROOT}/reference/lessons.md` (section 3D) always apply.

**Run:** `"<blender>" -b --factory-startup --python "${CLAUDE_PLUGIN_ROOT}/templates/blender/blocky/scene.py" -- "<abs table.md>" "<abs out_dir>/"`
with env `MODE=check | preview | stills (STILLS=40,110) | full`. **Always pass absolute paths** (a relative output folder lands
on the drive root). Blender path from `config.json`.

## The banks (templates/blender/blocky)
| Bank | What is in it | Change it in |
|---|---|---|
| Cast | hero (restyled every episode; optional eye colour), mayor, teacher, kid (smaller), inspector (the villain), mom, tinychef (tiny, for inside things); added 5 Nov 2026: **ginger** (the running gag, below), pip (the clumsy one in a yellow raincoat), grandpa, grandma, scientist (lab coat), guard (cap, hi-vis vest), chef, boss (suit), fan (copies fan#2, fan#3 ... each get another outfit, for a crowd); copies as tinychef#2 | `cast.json`; sheets with `cast_sheets.py` + `compose_sheets.py` (`KEYS=pip,dog` for just some) |
| Animals | dog, cat (an everyday grey tabby; Ginger is the only ginger one), rabbit (four legs), pigeon (a bird); same can head and faces; dog#2, cat#2 get another coat. Small characters are filmed closer and lower automatically. Moves: walk (a trot), run (bounding), jump, sit, fall (flops on its side), talk (bark, head nods), wave (a paw), laugh (happy bounce), cry (sad); pigeon: walk (pumping head), jump (startled flutter), fly (takes off and away) | `animals.py`; their moves at the end of `moves.py` |
| Faces | 12 expressions: calm, happy, laughing, shocked, scared, angry, sad, crying, smug, confused, sleepy, determined; 4 talk mouths; blinks every 2-4 s | `faces_bank.py` (draws the face pictures) |
| Moves | stand, walk, run, wave, point, talk, shrug, jump, fall, cry, sit, laugh, show (hold up), carry, yell, press (a lever), duel; athletic (13 Nov 2026): sprint (8.5 a second, steers exactly onto its 'to' spot), slide (feet first, 'speed N'), dive (superman dive and belly skid, 'land H' for a table top, 'speed N'), scoop (both arms grabbing fast); `a+b` puts b's arms and head on a's legs (`sit+cry`, `stand+wave`); 0.25 s blends; feet kept on the ground, smoothed | `moves.py` |
| Places | street (5 house types, shop, school, lamps, benches, cars), classroom, bedroom, kitchen, office, shop inside; each has named spots and ready camera framings | `places.py`; picture sheet with `place_sheets.py` |
| The RodiOcean lab | **lab**: the channel's own world and **the default world for every Short** (owner, 10 Nov 2026: "Yes, lab by default"): an underwater lab in light blue (light shafts, glassy bubbles, sea-blue sand with rippling light, soft far mounds) with a **huge screen** behind the cast, because the screen is what the videos are about. **The screen takes the video's shape** (owner: "The screen should be 9:16 for 9:16 videos"): upright 9:16 in Shorts, 16:9 when rendered wide (WIDE=1); give it a matching picture (Shorts: `boards_9x16/`, wide: `boards/`). Scene lines `light: underwater` and `screen: <picture or video file>` (a restyled board, a chart, a clip; videos play on the screen). Spots: left, centre, right (in front), presenter and screen_left (beside the screen). A close-up of the screen: a `mark` prop at the screen's centre. **No radar or sonar props in the lab** (owner: "AI always go to this radar when I talk about ocean"). **The channel's name lives on real things in the lab** (owner, 10 Nov 2026: "Subscribe @rodiocean more combined naturally with the surroundings like [the format benchmark]"): each thing is marked the way it really would be, worn a little, part of its own surface (never a sticker, never a corner logo). The lab's things (scene line `dress:`, default `crates, buoy, sub`): **crates** (left; "@RODIOCEAN" and "SUBSCRIBE" with cargo arrows, sprayed with a stencil), **buoy** (right; a lifebuoy on a post, "@RODIOCEAN" / "SUBSCRIBE" printed round the ring like a ship's name and port), **sub** (a mini research submarine parked far back right; RODIOCEAN in the owner's water letters on the hull, SUBSCRIBE under it), **tank** (left, instead of the crates; a fish tank with a fish), **hose** (left; a dive cylinder stencilled "@RODIOCEAN" with its hose across the floor). crates, tank and hose share the left side: one at a time. **The name goes on ONE thing per Short** (owner, 10 Nov 2026: "One per Short", hidden somewhere different each time, like the format benchmark): without a `logo:` line the scene file picks one of the things that are there (crates, buoy, sub, hose), so each episode gets its own spot; the build prints `LAB NAME ON: ...`. Name it with `logo: buoy` (also `floor` for worn floor paint, `pedestal` for a maker's badge, `none`); never two at once unless the owner asks, and don't use the same one two Shorts running. Background spots bg_left, bg_mid, bg_right for Ginger's cameo (Step 1c) | `places.lab()`, `lab_dressing.py`; the printed lettering `assets/brand/world_prints/` (make_world_prints.py); boards in `References/YouTube-AI-Motion-Graphics-RodiOcean/` |
| Props | toaster (pop, take, empty, glow, load), bread, toast, cloche (lift), pasta, ice, card (rise), frames (grow), bulb (on), spatula, mark (an invisible camera aim point); any prop hide/show; held in a hand with hold | `props.py` (added 5 Nov 2026 for the toast episode) |
| Story pieces (12 Nov 2026, the squirrel episode) | Props: satellite (glow, dim, squash, float `up N`, flash), cash (slide `to X Y Z`), maze, cage (`tall N`, `radius N`), shark (circle `around X Y; radius R; height Z; for S`), bubble (`icon squirrel|shark|scammer|satellite`; orbit `around X Y Z; radius R; speed REVS; phase DEG`, stop, flare, fade), magnifier (`hold <who>; tilt 125` with `stand+show`). Animal: squirrel (film it side-on: from the front it reads as a bear cub). Place: **void** = one flat colour (`void: #hex`, default light ocean blue), centred on 0 0, for acting a story out with no room around it (the format benchmark's plain-colour space) | `props_story.py`, `animals.py`, `cast.json`, `places.void()`; test table and stills in the squirrel episode's `blender/lookdev` folder |
| Light | day, golden, night (glowing windows, street lamps, ceiling lights indoors); underwater (for the lab: light aqua water, light from straight above) | `places.light()` |
| Camera | wide (fits everyone named), medium, close, two_shot, ots (over the first person's shoulder at the second), low, push_in, top (13 Nov 2026: straight down from above, a dollhouse floor plan; aim it at a 'mark' with 'size N' = 7 x N above the floor; the room's ceiling hides itself meanwhile); also frames a prop by its @name; every framing carries its own steady move (push, pull, swing, crane, slide; picked and tested automatically); 0.45 s flights; a change of place flies through a door | `scene.py` |
| Weekend pieces (13 Nov 2026) | cleaning: mess (tidy), unmade bed (make: the duvet spreads, the pillow flies home, a pop; lies on the bedroom bed 'at 236.8 1.4 1.16'), stopwatch 'lie 3.2' (big and face-up, for views from above), clock, microwave, tape, bars, shirt; ice: cube, tray, cup, clear block, cooler ('empty', fill, freeze), pot (boil, pour 'into @cooler'); light: lamp, switch, bow and arrow, dominoes, globe, conveyor, box | `props_cleaning.py`, `props_ice.py`, `props_light.py` (each file's top lists every action) |

**Re-render only what changed** (owner, 13 Nov 2026): plan a fix so the frames before it stay the same (new props 'hide' until their shot, people step out with 'away' instead of moving), check that the MOVE lines match the last run, then render just the changed frames with render_parallel's 'first-last'. Never run the picture tool (ComfyUI) while Cycles renders.

## Step 1. Restyle the hero for this episode (owner rule)
The hero changes with every episode to match the channel being reviewed: its colours and **one** signature item, never the
creator's face or likeness. The side characters keep their recipes. Put it at the top of the table as JSON overrides:
`hero: {"top": "#1d1d24", "pocket": "#f2f2f2", "accessories": [["cap", {"color": "#ff0033"}]]}`
(accessories: headphones, bucket_hat, cap (backwards), chef_hat, flat_cap, hair (bun), glasses (round/square), shades, tie, sash, backpack).
Render a sheet of the restyled hero (front, side, back, 3 faces) and get the owner's OK before the scene.

## Step 1b. The mystery hero until the reveal (owner, 5 Nov 2026)
Our series keeps the creator anonymous until the last line, so the hero can hide as the **mystery figure**: one inky shadow
over everything (body, hands, head and his signature item, so only the outline shows), a violet glow round the edges and a big
glowing yellow **?** for a face. It must read as a hidden shadow, never as a skin colour (the hands and head are the same ink as
the clothes, and there is no face). At the reveal he pops out of a ring of yellow, violet and white sparks as the restyled hero.
- In the table: put `reveal` in the hero's move at the reveal moment, e.g. `| 4.4 | hero | reveal+wave | happy | turn 0 | it's me |`.
  Before that moment he is the mystery figure; from it, the real hero. `mystery: yes` with no reveal keeps him hidden all scene.
- Reveal facing the camera (`turn 0`) with a `medium` or `close` camera row at the same time; keep others 2+ spots away.
- Approval pictures: `<projects>/short-factory-lookdev/blocky_mystery/mystery_sheet.py` (turnaround, the ? face, lineup with the hero it hides).

## Step 1c. Ginger, our running gag (owner, 5 Nov 2026)
Like a recurring character who falls in every video of a big channel, our own **Ginger** (a ginger tabby with a red collar and
a gold bell) shows up **once an episode** and does **the same fall**: the cat that never lands on its feet.
`| 6.2 | ginger | splat | determined | | |` - a butt-wiggle, a proud pounce, chin first into the ground with the back end up
and the tail swishing, then it topples onto its side, legs stiff, three stars circling; always 1.6 s, so viewers learn it and
wait for it.
- **The background cameo (owner, 10 Nov 2026), the default from now on:** Ginger is our version of the girl on the bicycle
  who falls over in most of the format benchmark's Shorts: a small character in the BACKGROUND, never the subject, never mentioned in the
  voice, there for viewers who spot it. In the lab: she runs in from off-shot behind the cast and splats; two rows:
  `| 0.8 | ginger | run | happy | bg_left; to bg_mid; only 0.8-6.0 |` then `| 2.6 | ginger | splat | shocked | | |`
  (or from `bg_right`). Pick a different second in each Short (not in the first 2 s of the hook), keep the camera on the
  story (the wide or a two-shot that happens to include the background), and never cut to her. The check reports her paws
  off the floor for a few frames while she topples: that is the fall, not a fault.
- **Bump and fall (owner, 10 Nov 2026: "I want the cat to bump something and then fall"), the cameo's other versions:** one row,
  `| 1.4 | ginger | run | happy | bump crates |`: she runs in from her side (bg_left, or bg_right for the buoy), hits the thing
  and falls; the thing reacts by itself (squash, a small white burst, then the stars). Four bumps, rotate them between Shorts:
  - `bump crates`: head first into the crate stack, thrown back paws up, lands on her side; the top crate rocks (move `bonk`).
  - `bump buoy`: into the lifebuoy's post; the ring swings on its hook (`bonk`).
  - `bump tank` (needs `dress: tank, ...`): pounces at the fish, hits the glass, hangs there, drops; the fish darts away (`smack`).
  - `bump hose` (needs `dress: hose, ...`): trips over the air hose and somersaults onto her side (`trip`).
  The run takes about 1-1.5 s, the fall about 1 s, the stars 1.6 s: start the row 3 s before the camera leaves that side. The
  things stand 3 units out from the middle, inside a Short's medium shot of someone in the centre, so the whole gag shows
  behind the cast. Showcases: `assets/brand/mark/showcase_bump_<thing>.mp4`.
- **Ginger's job in the story (only when the owner asks for it as a story beat):** whoever tries the obvious way (the WRONG
  BELIEF beat: "most people just ...") and fails, or a setback: Ginger pounces at the obvious prize and misses. Never in the
  first 3 s of the hook, never covering the subject.
- Film the whole fall in **one held shot** (a `two_shot` of Ginger and what it pounces at), then cut to a `close` on Ginger
  after the landing (1.4 s or more after the splat row). A close on someone lying down films them from in front automatically.
- A blank `do` keeps the current move, so `| 7.4 | ginger | | sleepy | | |` changes the face while Ginger stays down.
- Pip (yellow raincoat) can do a people's version of the same fall (`| 3.0 | pip | splat | shocked | | |`), but Ginger is the gag.
- Ginger is our own character: never a copy of another channel's character, name or look.
- Test: <projects>/short-factory-lookdev/blocky_cast2/ginger_test.md.

## Step 2. Write the scene table (free)
```
length: 15
light: day
hero: {...}
| at | who | do | face | where | says |
|---|---|---|---|---|---|
| 0.0 | place | street | | | |
| 0.0 | camera | wide | | hero, mayor | |
| 0.0 | hero | walk | calm | from -8 0.4; to left | |
| 2.8 | hero | stand+wave | happy | face mayor | hi mayor |
| 8.2 | place | classroom | | | |
```
- **at**: seconds. Take them from the voice's word times once the voice exists (each camera row lands on a phrase).
- **who**: `place`, `camera`, or a cast name (people or animals). Someone in a second place is a separate copy of them.
- **where**: tokens split by `;`: a spot (`left`, `right`, `bench`, `teacher`, `seat_0_2` ...), `from X Y`, `to <spot>` (walks or runs
  there and works out the time), `turn N`, `face <who>`, `seat N`.
- **says**: the words (mouth flaps now; real word times later).
- More **where** tokens: `at X Y Z` (an exact spot: on a table, inside a toaster), `to X Y`, `only A-B` (shown only then).
- **Props**: who = `@name`; the first row's do is the kind (`| 0.0 | @toaster | toaster | | at 278.6 0.85 1.21 | |`), later
  rows are actions (`| 0.0 | @toaster | pop | | | |`). In a hand: `| 2.5 | @toast1 | toast | | hold hero; until 8.2; tilt 125 | |`
  (tilt 125 with the `show` move keeps it upright). A camera row frames a prop: `| 0.0 | camera | close | | @toaster | |`.
- Kitchen table in the way? `| 0.0 | place | kitchen | | no chairs; no bowl | |`. Example table: the toast episode's scene_v1.md.
- Camera rows: `do` is the framing, `where` is who to frame. **A new camera row about every 1.5 s** (owner, 12 Nov 2026, the format benchmark's model Short has one every 1.4 s; the old rule was every 2-4 s), each landing on the word it shows; in a spoken list every item gets its own row. A row's time is when the camera ARRIVES; the flight into it starts 0.45 s earlier.
- **Every framing moves by itself** (13 Nov 2026, built into scene.py; owner: "most of [the format benchmark's] wins have nice camera movements across the whole video"). Each camera row gets one steady move: push, pull, arc_l / arc_r (swing round the subject), crane_up / crane_down, truck_l / truck_r (slide sideways, still aimed at the subject). The family changes every framing; a swing never circles a wide of a place or an over-the-shoulder; a `low` framing never cranes. Speeds are the format benchmark's measured ones: the room behind slides about 14 % of the picture width a second, pushes about 8 % of the distance a second; the move runs through the framing's middle (the planned picture) and carries on through the flights, so the camera never stops; a long framing moves slower instead of stopping. Each move is tried on the built scene first (faces in the picture at the start, middle and end, nothing in the way) and skipped if it fails; the check log prints `MOVE 3: medium -> arc_r`. Force one in the camera row's face column (`| 4.5 | camera | close | arc_l | hero | |`), or `still` for the old slow creep; `CAM=old` gives the camera before 13 Nov 2026 for comparisons. Measure every preview: `python scripts/camera_motion.py out.json preview.mp4` must show moving 90 %+ and longest still 0.3 s or less (lab test, squirrel Short first half: moving 99 %, still 0.0 s, sideways 12 %/s, zoom 6 %/s; old camera 88 %, 0.87 s, 3 %, 3 %).
- A change of place: the camera flies into that building's street door (school for the classroom, shop, a house for the
  other rooms), the picture fills with the door, and an identical door swings open into the room. Leaving a room is the reverse.
  Put the `place` row and the new place's first `camera` row at the same time.

## Step 3. Checks (free, about 30 s)
`MODE=check`. It lists every shot with its frames (`SHOT 3: 4.0-6.6 s, frames 106-199, close mayor`) and must say
**CHECKS: all clear** before any render:
- **FEET**: below the ground, or floating where they should stand;
- **OVERLAP**: two people's body parts inside each other in the same place;
- **FRAME**: a framed person's head is out of the picture;
- **FACE**: a framed person has their back to the camera (over-the-shoulder shots only test the face we look at).
- **BLOCKED**: someone or something stands between the camera and the framed face for most of the shot.
Fix the table (spots, turns, timing), never the check.

## Step 3b. Acting a story out (the 1-to-1 method, 12 Nov 2026)
- No board on a screen and no card props: the cast and props act each sentence. The narrator is off screen (no `says` rows) unless our host speaks as "I".
- Two tables joined in the edit are fine: the lab for the first half, `place void` for the half where the meaning is acted out (stages a few units apart along x, the camera flies between them). Reuse one stage for the ending with props that `hide` at 0 and `show` later.
- A tiny character (the squirrel, scale 0.125) runs proportionally slower (run = 5 units a second times its scale): start it next to where it must arrive, and give it `close` framings for its own moments. Film the squirrel side-on or three-quarter.
- Look at one still per framing yourself (`MODE=stills STILLS=...`, frame = 1 + seconds x 30) and fix what you see before any full render. Then deliver the video; do not stop to ask the owner at the stills.

## Step 4. Preview to the owner (about 1 minute for 15 s)
`MODE=preview`: half size, fast, no motion blur. Make an mp4 with the voice and send the phone copy. **Gate:** the owner
approves the timing and acting, or lists changes.

## Step 5. Full render (about 3 minutes for 15 s; a 30 s Short in about 6)
`MODE=full`, numbered folders (full_v1, full_v2 ...), keep every version. Settings are in `QUALITY` at the top of scene.py
(chosen by the speed A/B, see below).
- **Changed one shot?** Re-render only that: `SHOTS=3` (or `SHOTS=3,5`) with the same output folder; it renders the shot plus
  the flight into it and overwrites just those frames. If a character's row changed, re-render every shot that shows them.
- Then on to **sf-edit** (captions, music, whooshes) as usual.

- **Render in parallel** (12 Nov 2026): `python -I scripts/render_parallel.py <abs scene.md> <abs out_dir> 6` runs six Blenders on six stretches of frames (`RANGE=a-b` in scene.py): 531 lab frames in 80 s instead of about 15 minutes, identical pictures. A stretch can be re-rendered alone with `MODE=full RANGE=95-215`.
- **The chess look, last** (owner's bar: the chess Short): the same command with `LOOK=chess` in the environment and 4 workers: glossy marble checker floor, dusk sky in the void, warm key and cool rim, polished metal, AgX Punchy, background blur (premium.py). About 2-4 s a frame (54 minutes for 34 s), so only for the approved cut. `LOOK=premium` (pale, soft) was rejected.

## Speed A/B (5 Nov 2026)
The same 8 full-size frames (one per shot, motion blur on) with each setting (<projects>/short-factory-lookdev/blocky_speed):
| Setting | Seconds a picture | Change from the best | Verdict |
|---|---|---|---|
| ray tracing on, 48 samples (old) | 0.47 | none | the reference |
| **ray tracing on, 24 samples (now)** | **0.41** | invisible (0.17 of 255) | **chosen: 13% faster, same look** |
| ray tracing off, 48 / 24 / 16 samples | 0.44 / 0.36 / 0.41 | visible (about 2.2 of 255): the floors lose their soft shine | not worth it |
Rendering is not the slow part: building the scene takes about 10 s, a 15 s scene renders in about 3 minutes, a 30 s Short in
about 6, one re-rendered shot (3 s) in under a minute. Save time with the preview and with `SHOTS`, not with lower quality.

## Common fixes
| Problem | Fix |
|---|---|
| Someone floats or sinks | check the spot's height (street spots stand on the pavement, 0.06); sitting needs `seat N` or the place's seat height |
| A face is turned away | add `face <who>` or `turn N` to their row |
| Head out of the picture | name fewer people in the camera row, or use `wide` |
| Two people inside each other | move one to another spot; spots are 1.35 apart on the street |
| A flight crosses a wall | give the two shots more time apart, or frame from the open side of the room |
| Grass showing in a room | the room floor has an apron in front; if a new room shows grass, widen it in `room_shell` |

## Guardrails
- Free and local only: no paid 3D generators, no downloads without asking first.
- Never save over an original `.blend`; the scene is rebuilt from the table every run.
- No real faces or likeness. The hero's restyle uses colours and one item, never the creator.
