---
name: shorts-format
description: 'Make a complete ~30-second vertical 3D-animated explainer short on the measured format of a top faceless 3D explainer Shorts channel (29M subscribers, shorts with 124-255M views each) about a topic the owner chooses: topic and title on the format rules, script on the format spine, narration, look, keyframes, video, music, captions, edit, a format check against the measured numbers, and posting, all inside ElevenLabs/ElevenCreative with a price check before every spend. Use this whenever the owner asks for an "explainer short", a "what if" short, a "how does X work" short, a "format short", "make it on the shorts format", "the format spine", "format check", or gives a topic and wants a viral animated short, even if he only names the topic.'
---

# Shorts format: one ~30 s explainer, end to end

This skill turns a topic into one finished short that matches the measured recipe of the format benchmark (a top faceless 3D explainer Shorts channel). The recipe comes from a study of its 10 most-viewed shorts and all 4,099 of its short titles (29 Oct 2026). The data, frames and tools are in `<studies_root>/shorts-format` (study folder below). The full numbers are in `references/shorts-data.md`.

**What we copy is the craft, never the identity.** Never print the benchmark channel's name or logo, never copy its blue-headband mascot, never imitate its narrator's voice, and never remake one of its videos (every topic goes through the topic check). The brand on props is the owner's own channel name.

## Ground rules

- **Claude builds, the owner clicks.** Build board nodes, write every prompt, price with `estimate_only: true`. Never run a generation and never press Generate, Publish or "Run from here". The owner presses Generate after seeing the price (global CLAUDE.md; a settings hook enforces it).
- **Plain English to the owner:** short, lead with what changed, no paths or code unless asked, one clear question at the end.
- **One step at a time:** build only the current step's nodes, price them, let the owner generate and judge, then build the next step.
- Project folder per short: `<episodes_root>/<slug>/`, with a `JOURNEY.md` log of every decision, take and credit spent.

## The recipe in one screen (from his top 10)

| Part | Benchmark's number | Our target |
|---|---|---|
| Length | 23-40 s, typical 30 | 27-35 s |
| Words | 70-115, typical 85 (top 100: median 81, middle half 72-91) | 75-95 |
| Sentences | top 100: median 5 (4-6), 15 words each | 4-7, no fragments |
| First "But" | top 100: median 9 s (6.4-12.6), in 64 of 100 | 6-13 s in flips, stories, ladders; none needed in chains/guides |
| Glued sentences | top 100: 85 % of later sentences open with a glue word or point back | every sentence after the first |
| Speaking speed | 2.5-3.6 words/s, typical 2.8 | 2.6-3.0 |
| Voice starts | within 0.5 s, every video | frame one |
| Pauses over 0.5 s | 0 in 9 of 10 | 0 |
| Hard cuts | none in 7 of 10 (blurred swipes instead) | 0-2; scene changes are camera swipes |
| Voice above music | 9-22 LU, typical 16 | 14-18 |
| Music under voice | about 90 % of the time | the whole time |
| Sound effects | a few small whooshes | 2-5 in total |
| Captions | 1-3 words, white with a thin black outline, a bit below centre | same |
| Title | question or "How/Why/The reason…" + ONE emoji | same |
| Description, tags | none | one line + hashtags only |

## The model-Short method (owner, 12 Nov 2026: "a script 1 to 1 like [the benchmark's] videos")
The recipe above is the average of his top 10. For a new Short, also take ONE of his Shorts as the model and copy its skeleton exactly: number of sentences, words in each, the job and the linking word of each, where the voice speeds up or slows down, and a framing for every phrase. Measure it first (do not work from memory), put his sentences and ours side by side for the owner, and keep his last-line pattern (a return to the first picture that speaks about "us"). Full steps: skill **sf-pipeline**, "The 1-to-1 method". First model measured: "Why Your Brain Focuses On Negative Things" (studies/format_ref).


## The stages

### 1. Brief (free)
Ask only what is missing, in one message: the topic or area, the brand name to print on props (default: the owner's channel name), and the money mode:
- **Full:** every beat is generated video, about 40,000-50,000 credits.
- **Lite:** 2-3 hero beats are video and the rest are stills moved in the edit, about 18,000-26,000 credits.
Default to Lite for a first video. Always show the exact estimate before spending.

### 2. Topic and title (free) — read `references/topics-and-titles.md`
- Turn the owner's topic into **5 format angles.** Each is one concrete question a 12-year-old would ask, about something you can SEE: the inside of the body, a familiar object at an absurd scale, a "what if everyone/you…", or a strange true fact from war or history. Each angle needs a surprising, visual answer.
- Avoid what flops on his channel: celebrity and business gossip, tutorials, "the government doesn't want you to see this", and anything without a picture in it.
- Write each angle as his title formula: `How/Why/What If/Could/Can … ?` + one emoji (🤔 😮 😨 😱 🤨 😳 🤯).
- **Run the topic check** on all 5 (`python -I short-factory\scripts\topic_check.py --channel shorts-format "<title>" …`, using the Python set in config.json). Drop TOO CLOSE ones. For LOOK CLOSELY, read his title and change the angle if it is the same question.
- Show the 5 with one line each on the picture it gives, and recommend one. **Gate:** the owner picks.

### 3. Facts (free)
Research the answer from at least 2 reliable sources per number or claim (web search). Write `facts.md` with every claim and its sources. If a "what if" needs an estimate, show the arithmetic. A wrong fact in a 100M-view format is the fastest way to lose trust. **Gate:** none, but flag anything uncertain.

### 4. Script and beat sheet (free) — read `references/top-100-scripts.md`, then `references/script.md`
- **Name the story type first** (top 100: chain 28, myth flip 24, true story 16, secret reason 13, guide 10, ladder 5, fable 4). It decides the opener and whether a "But" is needed.
- Follow the spine: **"you" situation → wrong belief → "But…" → how it works, step by step → payoff and stop.**
  - The first 3 words name the subject. A cold open mid-action is fine for true stories and processes (29 of his top 100).
  - The "But" lands around 6-13 s in (median 9). Chains and guides may skip it and run on As / Once / Then / This.
  - Use linking words for the steps: "As… / Then… / Afterwards… / You see…".
  - End on a scale surprise or a human sting.
  - No "subscribe", no outro, no brand line.
- 75-95 words. Read time = words ÷ 2.8.
- **Beat sheet:** split the script into 5-7 visual beats (4-8 s each). Each beat lists:
  - its exact words;
  - the ONE picture that shows them literally;
  - the camera move;
  - how it leaves (swipe direction, or a fly-through an object);
  - Full/Lite: video or still.
- Plan the **loop**: the last picture returns to the first picture, so the short replays seamlessly. His biggest short does this. If the story can't loop, end on the biggest picture.
- Run **ec-hook-oracle** on line one plus a description of frame one. Fix until it scores 8 or more.
- **Story layer (story-scripts, short-form version):** write the common goal in one line; plant one question early that the last line pays off; turn every "and then" into "but" or "so"; mix sentence lengths; run the human-writing pass and `short-factory\scripts\script_check.py` until it shows no flags. The faceless-channel study's shorts test: put the viewer IN the problem in line one ("You run a giant company..."), unfold the fix step by step, reveal the real name at the end.
- **Gate:** the owner approves the script and beats.

### 5. Narration (≈100-300 credits) — read `references/prompts.md` (Voice)
- **One narrator voice for the whole channel.**
  - The owner designs it once in the ElevenLabs app (voice creation can't be done through the connector), using the Voice Design prompt in `references/prompts.md`.
  - Save its ID in the study folder (`channel_voice.txt`) and reuse it for every short.
  - Never clone or imitate a real person.
- **Make it sound human with natural-ai-voice in format mode:** mark up the script (one tag at the start, CAPS on at most one word per batch, commas and full stops only), split it into 2-3 batches, and have the owner generate **3 takes of each batch** (the Text to Speech page gives 2 free regenerations per batch). Comp the liveliest phrases with `short-factory\scripts\voice_comp.py`, then `--finish`. Check with `voice_check.py <voice.wav> format`. This replaces the old single node with the whole script.
- **Measure the take (free):**
  - length 27-36 s;
  - speaking speed 2.6-3.0 words/s;
  - no pause over 0.5 s (shorten gaps with ffmpeg silence trimming rather than re-rolling);
  - word times from Whisper (large-v3-turbo, word timestamps).
  These word times drive every cut and caption.
- **Gate:** the owner approves the read by ear.

### 6. Look and keyframes (≈3,000-7,000 credits) — read `references/prompts.md` (Look, Keyframe)
- One look block on every image, from `references/prompts.md`:
  - semi-real 3D;
  - one subject in the middle of a clean, empty set;
  - a soft pale-blue sky gradient, or a white-blue studio;
  - soft daylight, saturated but clean colour.
  For body topics: red muscle, blue and red vessels, yellow fat, glowing particles.
- **9:16** on gpt-image-2.5-sunburst, medium, 2K: one start frame per beat. A person who appears in 2 or more beats gets one character sheet first (≈85 credits), wired into each keyframe.
- **The brand goes on ONE prop**, the way he prints his name on armour, crates and fields. Make it readable and natural, never a corner logo.
- A keyframe is the FIRST moment of its beat, already mid-action. Frame one of beat 1 must already show motion or danger.
- **Gate:** the owner keeps each picture. Show prices first.

### 7. Video (Full ≈35,000-45,000; Lite ≈12,000-18,000) — read `references/prompts.md` (Video)
- Seedance 2.5, **480p, 9:16**, one take per beat, **audio OFF** (our own sound is added in the edit). Length = the beat's narration time + 0.5 s, minimum 4 s.
- Use the keyframe as the **start frame** (no other references allowed with a start frame). For the loop beat, also set the **end frame** = beat 1's keyframe.
- **One continuous camera per clip**, always moving: a push-in, a fly-through, an orbit, or a dive into a cutaway. Describe the motion, not the picture.
- End each clip with a fast whip or push with motion blur, in the direction the next beat starts from. That hides the join, his signature.
- Lite mode: stills get their motion in the edit (a slow push plus a 2-layer parallax), so only the hero beats are generated.
- Send the full parameter set on every node update (a partial update once reset a node to 720p and tripled its price). Re-set 9:16 after wiring anything.
- **Gate:** the owner locks each clip.

### 8. Music and effects (≈1,000 credits)
- One Eleven Music instrumental, 35 s, using the bed prompt in `references/prompts.md`:
  - light, curious, steady, 100-115 BPM;
  - no vocals, no build-ups, no drops.
- 2-5 sound effects: a soft whoosh for each swipe, plus one impact or pop only if the story has a physical hit.
- The video-editing sound pass: place effects with the voice and music muted, then set them low enough never to annoy. The benchmark keeps them sparse; keep his count.
- **Gate:** the owner approves by ear.

### 9. Edit in Remotion (free) — read `references/edit.md`
Build a new project at `<episodes_root>/<slug>/edit/`, pinned to the installed Remotion version. Never touch the owner's other projects. 1080×1920, 30 fps. One data file lists every beat's clip, trim and times.
- **Picture:**
  - clips trimmed to the narration's word times;
  - a 3-frame blurred swipe at each join;
  - a slow push on every hold;
  - Lite stills moved;
  - no title card, no end card.
- **Captions:** 1-3 words at a time from the Whisper word times, styled as in `references/edit.md`. They must never cover the subject's face.
- **Sound:**
  - the narration from frame one;
  - music under it the whole time, 14-18 LU below the voice;
  - whooshes on swipes;
  - no gaps.
- Sharpen 480p clips locally before the final render (4x-UltraSharp, as in ec-jingle-ad stage 11). Master at about **-12 LUFS, true peak -1 dB.**
- Number every render (v1, v2, …) and keep them all.

### 10. Format check (free)
- Run `python -I short-factory\scripts\format_check.py <final.mp4> short` (the Python set in config.json). It prints a table of ours vs his. Fix every NO with what you already have before spending again.
- Look at `format_check/hook.jpg`:
  - the voice is on frame one;
  - motion by 0.4 s;
  - the subject is alone and readable at thumbnail size.
- Run **ec-hook-oracle** on the real first 3 s. Aim for 8 or more.
- **Gate:** the owner watches the final.

### 11. Post
- Title as in stage 2 (question + one emoji, 4-8 words). A one-line description with 3-5 hashtags; no tag list.
- The cover is a striking mid-video frame with its caption showing: the subject large and the action clear.
- Switch on each platform's AI-generated label. Same file for YouTube Shorts, TikTok, Instagram Reels.
- Log the post date, then views after 24 h and 7 days, in `JOURNEY.md` so later topics learn from it.
- **The 24-hour rule (channel-playbook):** judge each short at 24 h on "viewed vs swiped away" (the faceless-channel study's winners: 80 %+) and retention (its winners: about 90 %+); don't wait for a flop to warm up. After about 10 shorts, write the channel's own "viral recipe list" from the top ones and redo it when views drop.

## Reference files
- `references/top-100-scripts.md`: the scripts of his top 100 measured (12 Nov 2026): the box, line one, the glue words, the seven story types, the endings. Data in `reference/creators/shorts-format/top100/`.
- `references/shorts-data.md`: every measured number, what each top short shows, title and topic statistics across 4,099 shorts.
- `references/topics-and-titles.md`: the topic generator rules, what wins and loses on his channel, title formula with examples.
- `references/script.md`: the script spine, linking words, timing maths, a worked original example and its beat sheet.
- `references/prompts.md`: the narrator voice design, the look block, keyframe and Seedance templates per beat type, music and sound-effect prompts.
- `references/edit.md`: Remotion edit spec (swipes, captions, sound levels, loop, sharpening, export) and the final checklist.

Source: our own analysis of public videos from Zack D. Films. Not affiliated with or endorsed by Zack D. Films.
