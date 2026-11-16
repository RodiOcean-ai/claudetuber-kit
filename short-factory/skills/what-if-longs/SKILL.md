---
name: what-if-longs
description: 'Make a complete 5-12 minute 16:9 YouTube video on the measured long-video recipe of a top faceless 3D explainer channel (2.8M-20M views) about a topic the owner chooses, built mainly as a "what if" video: a compilation of 6-10 what-if segments, a single what-if deep dive, or a true "harmless thing, terrible outcome" story. Covers topic and title, structure, script, narration, pictures, hero video shots, music, edit with music drops and swipes, thumbnail, description with chapters, and a format check against the measured numbers, all with a price check before every ElevenLabs spend. Use this whenever the owner asks for a "what-if long", a long "what if" video, a what-if compilation, a what-if deep dive, a "harmless thing, terrible outcome" story, a 3D explainer documentary, or a long version of the shorts, even if he only names the topic.'
---

# What-if longs: one 5-12 min video, end to end

This skill turns a topic into one finished long video that follows the recipe measured from the format benchmark's 10 most-viewed long videos (a top faceless 3D explainer channel) (study of 29 Oct 2026, in `<studies_root>/shorts-format`; numbers in `references/longs-data.md`). Picture, prompt and edit craft is shared with **shorts-format**. Read its `references/prompts.md` and `references/edit.md`; the differences for long videos are listed below.

**We copy the craft, never the identity:**
- no name or logo of the benchmark channel;
- no blue-headband mascot (the owner may create his OWN recurring host character);
- no imitation of his voice;
- no remake of his videos (run every segment through the topic check).

## Ground rules
- **Claude builds, the owner clicks.** Price everything with `estimate_only: true`; never run a generation or press Generate, Publish or "Run from here".
- **Plain English to the owner.** One step at a time, with a gate after each stage.
- Project folder: `<episodes_root>/<slug>-long/` with `JOURNEY.md` (decisions, takes, credits).
- **Money reality:** generated video costs about 1,300 credits per second at 480p, so 8 minutes of video would cost more than 600,000. A long video is mostly **stills moved in the edit** plus a few **hero video shots**. Show the owner the plan and its price before stage 6.

## His long-video recipe in one screen

| Part | His number | Our target |
|---|---|---|
| Length | 3:05-27:21; best 5:24-6:33 (deep dives), 12:13 (compilation) | deep dive 5-7 min; compilation 8-12 min |
| Opening | premise at 0 s, no intro, no "hi guys" | same |
| Speaking speed | 2.25-2.7 words/s, typical 2.55 | 2.5-2.6 |
| Voice covers | 88-92 % of the running time | about 90 % |
| Picture changes | 6-14 hard cuts/min; in 3D a new view every ~1.5 s through camera flights | a new view every 2-4 s |
| Voice above music | 7-15 LU, typical 12 | 11-14 |
| Music | under 75-94 % of the time; **pulled to near-silence before reveals** | same |
| Captions | none on screen (16:9 is clean) | none; upload an SRT for closed captions |
| Call to action | none spoken | none; ask in the description only |
| Thumbnail | one strange bright image, no text in 7 of 10 | same |

## Choose the format (stage 2 decides)
- **A. What-if compilation (recommended for "what ifs"):** 6-10 self-contained what-if segments, 45-90 s each, chained with no host and no title cards. Model: "13 Unreleased Videos…" (11.2M). Each segment can also be cut into a 9:16 short, so every credit works twice.
- **B. One what-if deep dive:** one huge question followed through escalating stages ("the first second… the first hour… a year later"), 5-7 min. It uses the documentary devices from his top stories: the cold open, a black beat, a planted second thread, pivot lines, and a held-back payoff.
- **C. True "harmless thing, terrible outcome" story:** a paradox topic (balloons + disaster, a soda contest + deaths, a gas pedal + a $2.3B fine), 5-6 min. This is his strongest long format (20M, 12.5M, 10.6M). Facts and sources matter even more here.

## The stages

### 1. Brief (free)
Ask, in one message:
- the topic or area;
- the format (A, B or C; default A);
- the brand for props;
- whether the owner wants his own host character;
- the money tier:
  - **Lite:** 1 hero video shot per segment or section, everything else stills. About 70,000-110,000 credits for 8-10 min.
  - **Rich:** 2-3 hero shots per segment. About 150,000-250,000.

### 2. Topic, title and structure (free) — read `references/structures.md`
- **A:** generate 12 what-if segment ideas with the shorts-format topic rules, then topic-check them (`short-factory\scripts\topic_check.py`). Keep 6-10 and order them:
  - open on the strongest question as a picture;
  - alternate light science with darker ones;
  - hold the thumbnail segment back to about 80 % of the running time;
  - end on the most mind-bending one.
- **B and C:** one premise. Run the topic check and a web search to confirm it's fresh and true. Then build the stage ladder (B) or the story beats (C) from `references/structures.md`.
- **Title:** use the formulas in `references/packaging.md`. **Gate:** the owner approves the title, the segment list and the order.

### 3. Facts (free)
Research every claim from 2 or more sources. Write `facts.md` and a public **sources document** (he links one in the description). Show the arithmetic for every estimate.

### 4. Script (free) — read `references/structures.md`
- Write the whole narration as one document with section markers and target times, at 2.55 words/s (6 min = about 920 words; 10 min = about 1,530).
- **Hook rules:**
  - line one states the premise with a number, date, place or the what-if itself;
  - the stakes come within 25 s;
  - for B and C, a 1-2 s black beat follows the stakes line.
- Every section ends on a **pivot line** from the phrase bank, and every segment ends on its biggest line.
- Run **ec-hook-oracle** on the first 30 s; aim for 8 or more.
- **Story layer (story-scripts):** plan first (common goal, surface and deeper problem, thumbnail draft before the script, research gaps). Formats B and C run on the story-scripts hero's-journey map (the crisis is where the deeper problem shows; the twist reframes the topic at the end). Every segment plants a question it pays off. Then the five rewrite tactics (simple → complex, let the viewer figure it out, but/therefore, rhythm, edit notes) and the human-writing pass; `short-factory\scripts\script_check.py` must show no flags.
- **Gate:** the owner approves the script.

### 5. Narration (≈1,000-3,000 credits)
- Use the channel narrator voice (`<studies_root>/shorts-format/channel_voice.txt`; designed once with the shorts-format Voice Design prompt).
- **Use natural-ai-voice (format mode for the long format):** mark up the script, split it into batches of 2-4 sentences, and have the owner generate each batch on the Text to Speech page, keeping all 3 takes (1 paid + 2 free regenerations). Comp with `short-factory\scripts\voice_comp.py`, keeping `||` holds only where the edit has a music drop or black beat, then `--finish`. Check with `voice_check.py <voice.wav> format-long`. This replaces the single long read.
- **Measure (free):**
  - words per second 2.4-2.7;
  - voice covering 85 % or more of the time (trim gaps longer than 0.8 s, but keep the planned black beats);
  - Whisper word times, which drive every picture change.
- **Gate:** the owner approves by ear.

### 6. Picture plan and price (free) — read `references/structures.md` (picture plan)
- Split the narration into **views of 2-4 s**, one literal picture per phrase: about 15-25 views per minute.
- Mark each view as one of:
  - a **hero video** (a flight, an impact, a transformation; the money shot of each segment);
  - a **still** (moved in the edit);
  - a **reuse** (the same still, re-framed or zoomed);
  - a **graphic** (a map, a timeline, numbers, built free in Remotion).
- Price the plan with `estimate_only` and show a table: stills × price, hero seconds × price, music, total. **Gate:** the owner approves the plan and the total.

### 7. Look, characters and stills (≈30,000-60,000 credits)
- **Look block:** the shorts-format look block, with "Horizontal 16:9 composition, subject in the centre third" instead of 9:16. Keeping the subject in the centre third lets every segment be re-cropped into a 9:16 short later.
- Two scene worlds, as he uses them:
  1. a **blue explainer world** (a pale-blue backdrop or a bright blue grid floor) for mechanisms and what-if physics;
  2. **fully built locations** (a street, a stadium, a hospital, a trench) for stories.
  Orange-red is kept for heat, danger and death.
- Character sheets first for anyone in 2+ views (the owner's host included). Brand props: put the brand on 1-3 props across the video (a mug, a crate, a scorecard, a shirt), never as a corner logo.
- gpt-image-2.5-sunburst, medium, 2K, 16:9. Make stills **in segment order, one segment at a time**, with a gate after each segment.

### 8. Hero video shots (Lite ≈15,000-50,000; Rich ≈100,000+)
- Seedance 2.5, 480p, 16:9, audio off, start frame = its still. 4-8 s each.
- One continuous camera move, using the shorts-format video template. For a segment change, end the clip with a whip or fly-through toward the next segment's world.
- One take each, owner reviews, then the next one.

### 9. Music and sound (≈2,000-5,000 credits)
- **Music:** one bed per mood, 60-120 s each, looped and crossfaded in the edit (prompts in `references/structures.md`):
  - light curious for science;
  - dark strings for stories, which he uses even under "happy" moments to warn the viewer.
- **Sound effects:**
  - a whoosh for every segment change and camera flight;
  - impacts on physical events;
  - a low heartbeat pulse under rising tension;
  - one or two signature sounds per segment (a siren, a ding, a stomach rumble).
  Target about 7-10 a minute.

### 10. Edit in Remotion (free) — shorts-format `references/edit.md`, with these changes
- 1920×1080, 30 fps. No burned-in captions; export an SRT from the Whisper words and upload it as closed captions.
- **Every still moves:**
  - a slow push of 1.00 → 1.06 over its view;
  - a 2-layer parallax on hero stills;
  - a drift sideways on wide shots.
  Nothing holds still for more than 4 s.
- **Joins:**
  - inside a segment, hard cuts on the narration's phrase boundaries, or the 3-frame blurred swipe;
  - between segments, an object or camera wipe (fly through a cloud, glass shatters into the next scene, a page blows across the frame) with a whoosh. **Never a title card.**
- **Music drops:** before every reveal and on each black beat, pull the music to near-silence (-35 to -40 LUFS) for 0.5-2 s, then hit the reveal line. One segment in a compilation may run with no music at all (his claustrophobic coffin piece), for contrast.
- **Graphics (free):** maps with a red glow, timeline counters ("1 second later…"), big numbers, and a highlighter sweep on a newspaper-style clipping for true stories.
- **Mix:**
  - narration -14 LUFS, compressed to a loudness range of 4 LU or less;
  - music 11-14 LU below;
  - master about -12 LUFS, true peak -1 dBTP.
- Sharpen the 480p hero clips and the 2K stills to 1080p locally before the final render.
- A sponsor, if any, is written INTO a segment as a story move, never as a break.
- **Editing layer (video-editing):** colour-code the script into picture types before building; lay music right after the narration so cuts land on beats; eased moves with a fixed focus point across cuts; something new on screen every 2-4 s even in long holds; the sound-effect pass done with voice and music muted; simple Remotion motion graphics (maps, counters, flowcharts with drawn lines and glow). Keep the benchmark's clean look: no light leaks, no text pops over the 3D.

### 11. Format check (free)
- Run `python -I short-factory\scripts\format_check.py <final.mp4> long` (the Python set in config.json) and fix every NO.
- Watch the first 45 s and every segment change: no dead air, no frozen frame, the payoff line lands on its picture.
- **Gate:** the owner watches the whole video.

### 12. Package and post — read `references/packaging.md`
- **Thumbnail:** one strange, bright 16:9 image of the held-back segment, made on gpt-image-2.5 (16:9 2K). No text, or 2-3 huge words. Apply **thumbnail-design**: thirds layout, the channel's 5-colour palette with this video's highlight colour, darkening behind the subject and text, a light glow (`short-factory\scripts\thumb_finish.py`), and its home-page preview at real size and at 160 px.
- **Dubbing (optional, after 7 days):** the natural-ai-voice dubbing stage, into Spanish, Hindi and Portuguese audio tracks.
- **Title** from the formulas; **description:**
  - a 1-2 sentence teaser ending on a question;
  - a sources link;
  - chapters (from the section times);
  - a "some scenes are AI-animated / dramatized" line;
  - 6-12 literal search tags.
- Switch on YouTube's altered/synthetic content label.
- **Cut 9:16 shorts** from the best 2-3 segments (re-frame the centre third and add shorts-format captions), and post them in the following days with "full video on the channel" in a pinned comment.
- Log the views after 24 h, 7 days and 28 days in `JOURNEY.md`.

## Reference files
- `references/longs-data.md`: the numbers, what each of his 10 long videos did, and why the top ones won.
- `references/structures.md`: templates for formats A, B and C, the segment template, the pivot-line phrase bank, the picture-plan maths and the music prompts.
- `references/packaging.md`: thumbnail rules and prompt, title formulas, the description template with chapters, tags.
- Shared from shorts-format: `references/prompts.md` (voice, look, keyframe, video and sound prompts), `references/edit.md` (edit and mix), `references/topics-and-titles.md` (topic tests).
- The full per-video breakdowns: `<studies_root>/shorts-format/analysis/L01…L10/breakdown.md`.

Source: our own analysis of public videos from Zack D. Films. Not affiliated with or endorsed by Zack D. Films.
