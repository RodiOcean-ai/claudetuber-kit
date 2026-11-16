---
name: sf-thumbnail
description: The thumbnail for a short-factory Short - Claude writes a GPT-image-2.5 prompt (one centred hero, the subject as anonymous silhouettes, top third empty for text, no text and no faces), builds the node in ElevenCreative and prices it with estimate_only, the OWNER presses Generate, then the 0-3 glowing words are added locally and checked at phone size; documentary-thumbnail rules; 16:9 version for long videos. Use whenever the owner says "thumbnail", "cover", "cover image", "make the thumbnail", "thumbnail prompt", "add the text to the thumbnail", "13 BILLION / WHO?", "does it read on a phone", or when sf-pipeline reaches stage 7.
---

# Thumbnail: the owner generates, Claude prompts and finishes

The image is made with **GPT-image-2.5** inside ElevenCreative (the owner's credits). The text is added locally, for free, so it is sharp and spelled right.

Plain English to the owner, no paths or code, one question at the end.

> **Money rule (never weakened):** Claude builds the node and prices it with `estimate_only: true`. Claude never runs a generation and never presses Generate. A settings hook enforces this. The owner presses Generate, after seeing the price.

## The series look (from the documentary-thumbnails study and our two episodes)
Read `${CLAUDE_PLUGIN_ROOT}/reference/creators/documentary-thumbnails/NOTES.md`. In short:
1. **ONE hero, centred, big.** Symmetry: props balanced left and right, a loud background (rays, fire, a cracked giant object).
2. **The topic readable in 0.1 s:** one icon of the subject's world (a red play button, a water bottle), never a real logo.
3. **Hyper-saturated painted 3D look**, deep shadows, strong rim light; orange/teal or red/yellow.
4. **0-3 words of text**, glowing, added locally. Recent thumbnails of the studied documentary channel often have none.
5. **The series rule:** the creators stay **anonymous** (silhouettes from behind, no faces, no names). The cover keeps the mystery; the last line of the video reveals who.

## The channel brand (RodiOcean "Sonar" look; `${CLAUDE_PLUGIN_ROOT}/assets/brand/BRAND.md`, owner's picks 10 Nov 2026)

> **Shared kit:** the RodiOcean brand files (logo, name prints, sounds, backgrounds, letter font) are not included. Put your own files in `assets/brand/` with the same names (see its README), or leave the brand off. Your own brand sheet `assets/brand/BRAND.md` (made with the **yt-branding** skill) wins: when it exists, use its colours, fonts and text style instead of the house look below.

- The cover text keeps the house style above (lemon yellow, orange glow). **Yellow means "measured"**: the headline and measured numbers only.
- A card or cover with **no generated picture** (text cards, long-video title cards, end screens) uses the standard background **A "Ocean light"** with the light-blue touch: `assets/brand/templates/bg_A_ocean_rays_wide.jpg` / `_tall.jpg`.
- Add the proof readout (`assets/brand/make_brand.py readout "x42"`) to a cover only when the measured number IS the hook.
- The owner's own water-letter font (`assets/brand/letters/`, set with `water_line` in make_brand.py, one straight baseline) is for one word at a time (SUBSCRIBE, FOLLOW), never for sentences or cover headlines.
- The channel's profile picture is the owner's own water-splash RO logo (he kept it over the sonar logo); never redraw it.

## Step 1. Write the prompt (free)
Fill this template (our first episode's prompt, made general). Save it as `post/THUMBNAIL_PROMPT.md` with the text plan underneath.

> Vertical 9:16 YouTube Shorts cover, hyper-saturated painted 3D illustration, symmetrical, one centred hero moment. **[Who, anonymous]:** shown only as solid black silhouettes from behind, [pose], in [everyday setting] at golden hour; their faces are never visible. **[Hero object]** hangs mid-air in the centre, glowing, with motion streaks. Behind them, **[the subject's icon, e.g. a huge glossy red play button]**, cracked down the middle, warm light bursting through. Around them, frozen mid-air: **[2-3 small props from the story]**. [Two-colour] palette, strong rim light outlining the silhouettes, deep vignette. **Keep the top third darker and empty for large text.** No text, no logos, no faces, no real people's likeness.

Checks before building: one hero, nothing that names the creator, no child's face, props from our own story, the top third clear.

## Step 2. Build and price (free)
- **Confirm the model id first** with `creative_get_model_guide` (GPT-image-2.5; the exact id and its options change, e.g. a "sunburst" variant). Then `creative_get_model_schema` for the settings.
- Build one image node on the episode's board (or a new "<slug> thumbnail" flow): 9:16, medium quality, 2K, 2 variations if the price allows. Attach a reference image only if the story needs a specific icon (the red play button reference is `assets/images/red_button_ref.png` (not included in the shared kit: use your own reference picture)).
- Price it with `estimate_only: true`. Tell the owner the price and the board name. **Gate:** "It's built and costs about N credits. Would you press Generate on the thumbnail node?"
- When he has generated: read the result, download it into `post/` (ask first if it is a download outside the board), and log the credits: `tracker.py credits <slug> <amount> "thumbnail"`.

## Step 3. Finish locally (free)
- **House text style (owner, 7 Nov 2026): lemon yellow (from the thumbnail-design study), Impact (blocky, tall), 3D edge, no outline, orange glow on every line** (all the tool's defaults). One line filling the width with --size-max 700: about 30 % of the picture height for 12 letters (the thumbnail-design study: ≈ 23 %). Shrink the picture toward the bottom-right (about 78 %) so the hero's head only tucks under the bottom of the letters.
- **Expression (owner's rule):** the block hero gets a moulded cartoon toy face with a gritted-teeth grimace ("a simple cartoon toy face moulded on it: a dramatic gritted-teeth grimace, a wide row of white clenched bared teeth, big wide stressed eyes, eyebrows pushed together"); negatives: smiling, happy, realistic human face, human skin, nose, hair, real person. A toy face only, never a real person's likeness. Short words that can't be misread; big; never over the hero or the key object.
- **Expression, updated (owner, 11-12 Nov 2026):** he picked the **excited** face over the gritted-teeth grimace on two covers running ("an excited amazed expression, a huge wide open-mouth grin showing white teeth, big sparkling wide eyes, eyebrows raised high"): prompt it from the start. To change only a face on a picture he likes, use the local face-edit tool. **Words:** he picks the picture first, then the word from three or four options RENDERED on that picture (never a list in text); the word should add what the title leaves out ("STEAL THIS", "NO ENEMY").
- **Text behind the character (owner's pick, from the thumbnail-design study):** make a mask of the hero (hero_mask.py, by colour) and pass it to thumb_finish.py --front; one big line across the top, the head tucked under the bottom of the letters, the word still readable.
- **Local option (owner, 7 Nov 2026: "use local"):** the picture itself can be made free on this PC with ComfyUI (<your-picture-maker>/make-picture.py, Qwen-Image 2512, about 6 s each, 1664x928 for 16:9). Ask for "one single continuous scene, no panels" and a blank featureless head, and check every seed for split panels, faces and fake UI.
- Vertical Shorts cover: `thumb_vertical.py <in> <out> --line1 "13 BILLION" [--line2 "WHO?"]`
  - line 1: the big number or claim, glowing yellow with a dark edge and orange glow;
  - line 2 (optional): one short white word that opens the question ("WHO?", "HOW?").
  - It also lifts contrast and colour and adds a vignette. Output `post/THUMBNAIL_FINAL.jpg` (1125x2000 or larger).
- Long video (16:9): `thumb_finish.py` with the same rules (hero on the right third if a mascot is used; see **thumbnail-design**).
- Text never covers the hero, and stays clear of the platform's button zones.

## Step 4. Phone-size check
- Long videos: phone_view.py draws two phone screens (home feed full width and the small Up next list) with other creators' covers named creator_x.jpg; use their real titles.
- Make a feed-size copy (about 180 px wide) next to two random Shorts covers, and look at it: can you tell what it is and read the words in one glance? Is the hero still the first thing the eye lands on?
- Optional: ask **hook-oracle** to score the cover as a first frame (tests 1, 2, 3, 5, 6, 7).
- Save `post/thumb_phone_size.jpg`. **Gate:** the owner picks the final thumbnail.

## Also: the in-app cover frame
Some apps only let you pick a frame. Use **sf-posting** (`covers.py`) for 2-3 strong mid-video frames with their caption showing (subject large, action clear).

## JOURNEY.md lines (dated)
Prompt version, model id confirmed, price shown, the owner generated (credits), which variation, the words added, phone-size verdict.
