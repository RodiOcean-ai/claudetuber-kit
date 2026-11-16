---
name: thumbnail-design
description: Design a YouTube thumbnail with a measured method (from our study of a faceless channel whose thumbnail guide has 1M views) - rule-of-thirds layout, a 5-colour channel palette with a changing highlight colour, one uncommon font, combining 2-3 of the 10 proven thumbnail types, inspiration from outside the niche, 1-3 glowing words or a big number, then finishing (darken behind text, recolour, light, glow) and a home-page test - built with ElevenCreative image models plus free local finishing, with a price check before any spend. Use whenever the owner asks for a thumbnail, cover image, thumbnail ideas, A/B thumbnails, a channel look/palette, "make the thumbnail pop", "which thumbnail type", or when a shorts-format or what-if-longs video reaches packaging.
---

# Thumbnail design: thirds, palette, 2-3 proven types, a local finish

From the studied creator's "How I Actually Make Viral Thumbnails" (I01, 1.06M views, his most-viewed video) and his 9 thumbnails (faceless-channel study of 29 Oct 2026; contact sheet in your own study folder, `<studies_root>/faceless-channel/thumbs/all_thumbs.jpg`, not shipped).

**Copy the craft, never the identity:** no ginger bearded man in a suit with a red tie, no YouTube-logo pin, no copy of his yellow-glow look as a whole. Our channel gets its own mascot or no mascot, and its own palette.
**Claude builds and prices, the owner presses Generate.** Price every image with `estimate_only` first.

## Why it matters
"If no one clicks, no one watches." The thumbnail is drafted **before** the script (story-scripts stage 1) and the video must deliver its promise.

## What the studied creator's 9 thumbnails do (measured)
- **The same mascot in every one,** placed on the right third line, serious face, looking slightly off-camera. It brands the channel at a glance.
- **Text in 6 of 9:** one or two words in huge bold yellow capitals with a strong glow, along the top ("THUMBNAILS", "EDITING", "20M VIEWS", "ONE VIDEO", "VIRAL SCRIPT", "REAL AI VIDEO"). It names the topic or the big number; it never repeats the title.
- **No headline in 3 of 9:** the story is carried by one prop (a microphone labelled "AI VOICE", a phone with a pixelated face and "1.6M ↑", a red button with "+196.4k ↑").
- **Big numbers in 4 of 9** (20M, 1.6M, +196.4k, a rising chart).
- **Palette:** black/dark navy + white + yellow as the constant, one highlight per video (red, blue, teal, orange fire). Glow on every edge.
- **One prop that tells the story,** held toward the camera or exploding behind (burning pen, nuclear chart, flowchart of hidden steps).
- **Hidden detail:** pixelated face (I04), blurred step boxes. The viewer must click to see it.

## Stage 1. Channel kit (once per channel)
- **Rule-of-thirds grid** on every design: the subject's face or the prop sits on a third line, text along the top third.
- **Palette of 5:** one main colour (his: yellow), black, white, one mid tone, and **one highlight that changes every video**, so each looks fresh but stays recognisable.
- **One font** that's bold and not overused (his is a geometric display font). Owner's decision, 7 Nov 2026: our covers use his lemon yellow and 3D edge on purpose, with Impact as our own blockier font; his mascot and identity are still never copied. Same text style every time: bold capitals, fill, outline, outer glow.
- Save the kit in the channel's brand sheet, `assets/brand/BRAND.md` (skill **yt-branding**); if one exists already, start from it instead of making a new kit.

## Stage 2. Concept (free) — read `references/thumbnail-types.md`
1. Write the one feeling the viewer must get in a split second (shock, curiosity, greed, "that can't be true").
2. Pick **2-3 types** from the 10 and combine them (big number + header + hidden detail is his favourite). Keep one combination for about 5 videos, then rotate, so the audience learns the style without it going stale.
3. **Look outside the niche.** List 5 thumbnails from popular channels in other niches (on the YouTube home page). If ours looks like every other thumbnail on the same topic, it loses.
4. **Text:** a big number, a bold claim that goes against common belief, 1-3 words naming the topic, or nothing. Never the title again.
5. Sketch 2 versions (A and B) as a short written layout: where the subject is, the prop, the text, the highlight colour.
Gate: the owner picks.

## Stage 3. Make it (≈600-1,100 credits per image; estimate first)
- **gpt-image-2.5-sunburst** (or gpt-image-2 when exact text matters), 16:9, 2K, medium. Prompt with `references/prompts.md`: layout on thirds, the prop, the palette, the glow, and **the text written exactly** in quotes, or "no text" and add the text locally.
- For a recurring mascot, wire its character sheet as a reference (ec-character-refs).
- One take, the owner reviews, then the next.

## Stage 4. Finish locally (free) — the study's Photoshop steps, done in our tools
`short-factory\scripts\thumb_finish.py` (in the plugin's `scripts` folder) does each step as an option:
- **Text style:** fill + dark outline + outer glow in the main colour (if the text is added locally).
- **Darken behind the text and subject:** a big soft dark brush at about 5 % strength, painted on its own layer behind the words and the face, so they read on any background.
- **Background colour shift** (hue/saturation) to match this video's highlight.
- **Blur or pixelate** the hidden detail (Gaussian or mosaic).
- **Light reflection:** a soft coloured glow where the light comes from, blended as overlay, so pasted elements belong to the scene.
- **Final colour pass:** contrast and saturation up a touch (his Lightroom step).

## Stage 5. Test (free)
- `thumb_finish.py --preview` puts the thumbnail and title into a mock YouTube home-page grid at real size (and at 160 px wide) next to 8 other thumbnails. Look for: the subject readable, the text readable, the colour standing out.
- He uses the free site thumbsup.tv for the same check; the owner can use it too.
- After posting: YouTube's "Test & compare" with the A and B versions.

## Rules for shorts-format and what-if-longs videos
The format benchmark's long videos win with **no text in 7 of 10** and one strange bright image. Combine: the format benchmark's single impossible image + this method's thirds layout, palette discipline, darkening and glow, and this method's types "hidden detail" or "big number" only when the video has one. Shorts don't need a custom thumbnail.

## Reference files
- `references/thumbnail-types.md`: the 10 types, with the study's examples and when to use each.
- `references/prompts.md`: image prompts for each type, the text block, the mascot block.

Source: our own analysis of public videos from Isaac (@isaacverse). Not affiliated with or endorsed by Isaac or @isaacverse.
