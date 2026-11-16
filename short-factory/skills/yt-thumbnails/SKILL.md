---
name: yt-thumbnails
description: Make a YouTube thumbnail a stranger gets in one glance, for beginners, for long videos and Shorts covers - one hero and one idea, 0-3 words that add what the title leaves out, the cover-the-text test, strong colour contrast and rim light, text behind or around the subject, first seconds of the video that match the picture, a phone-size check at feed and up-next size next to real competitors, how to make it (Claude writes the picture prompt, you run the picture maker of your choice, Claude adds the words locally with the kit's scripts), how not to look like AI slop, and YouTube's current sizes and A/B testing. Use when the person says "make a thumbnail", "thumbnail ideas", "thumbnail prompt", "does my thumbnail work", "thumbnail text", "cover image", "Shorts cover", "it looks like AI", "phone check", "A/B test the thumbnail", or when a video reaches packaging. Inside /make-short, sf-thumbnail runs these steps for Shorts; thumbnail-design holds the deeper craft; packaging-critic scores the result.
---

# YouTube thumbnails: one glance, one idea, one promise

**For Claude:** plain English, one step at a time, one clear question at the end. Show choices as pictures, not lists
(three words rendered on the picture beat three words in a message). **Never press Generate in a paid tool and never
spend the person's credits:** write the prompt, they run it. Never upload.

## The one idea
People see the thumbnail before they read the title. In one glance at phone size a stranger must know **what it is
about** and **why to click**. The thumbnail, the title and the first 5 seconds make **one promise** (see **yt-titles**).

## The 8 rules
1. **One hero, one idea.** One thing the eye lands on first: a character, an object, a big number. Everything else
   supports it or goes. Remove things until it stops working, then put the last one back.
2. **0-3 words that add.** The words say what the title leaves out, never the same words.
   Title "How to Make Animated Shorts with Free AI" -> thumbnail "$0" or "1 EVENING", not "FREE AI SHORTS".
3. **The cover-the-text test.** Cover the words: does the picture alone still carry the idea or the feeling? Then cover
   the picture: do the words mean something? Each half must work, and together they must make one point.
4. **Strong contrast.** A bright hero on a dark background, or dark on bright. One **accent colour** (from your brand
   sheet) used only on the thing that matters. Check it in black and white: the hero and the words must still stand out.
5. **Rim light.** A thin bright edge of light around the hero lifts it off the background. Ask for it in the prompt
   ("strong rim light outlining the subject"), or add a glow when you finish it.
6. **Text behind or around the subject.** One big word across the top, the hero's head slightly in front of the bottom
   of the letters, gives depth. Never cover the hero's face or the key object. Keep the bottom-right corner clear
   (the video's length is printed there).
7. **Mid-action, a little conflict.** Something is about to happen: about to fall, break, win, explode.
8. **The first seconds match.** The video's opening shot shows the thumbnail's scene (or the same object) within
   5 seconds. A thumbnail the video never shows is the fastest way to lose viewers.

## Step 1. The brief (free)
Write five lines:
- the **title** (or the 2-3 titles you are testing);
- the **one feeling** in a split second: curiosity, shock, "I want that", "that can't be right";
- the **hero** and what it is doing;
- **3 word options** (0-3 words each), each adding something to the title;
- the **colours and font** from the brand sheet (`assets/brand/BRAND.md`, skill **yt-branding**).

## Step 2. Look at the competition (free)
- Search your video's main search line on YouTube. Save 6-8 thumbnails from the results and the "up next" list around
  your topic into a folder, named `<channel>_<video>.jpg`. They are for your private check only; never reuse them.
- Write down what they **all** do. Then do something different: if they are all busy, go simple; if they are all red,
  go blue; if they all show faces, show one object.
- Look outside your niche too: the YouTube home page shows what grabs eyes this month.

## Step 3. Three concepts in words (free)
For each concept: the hero, the action, the background, the words and where they sit, the accent colour.
Claude scores each on the checklist below; you pick one. Ideas for concepts: a big number, before/after, one strange
object, something hidden or blurred, the hero next to something huge (more in **thumbnail-design**'s 10 types).

## Step 4. The picture (Claude writes the prompt, you make the picture)
A prompt template (16:9 for a long video; for a Shorts cover say "vertical 9:16"):

> 16:9 YouTube thumbnail, [your style, e.g. bright painted 3D / flat 2D cartoon / clay], **one [hero]** [doing the action],
> large and slightly right of centre, mid-action. Simple [background] in [base colour]. Strong rim light outlining the
> hero, one [accent colour] [object] as the only bright accent. **Keep the top third calm and empty for large text.**
> No text, no letters, no logos, no watermark, no real person's face or likeness.

- **You run it** in the picture maker you choose: a free one on your own PC (for example ComfyUI) or a paid website
  (your account, your credits, your decision). Make 4-8 versions.
- **Pick at small size, not full size.** Shrink them all to thumb size and choose the clearest, not the prettiest.
- **Even better, use your own video:** a frame from your own animation, cleaned up and lit, is yours, matches the
  opening by definition, and never looks generic. A mascot built in code (**explainer-2d-character**,
  **sf-blocky-world**) looks the same in every thumbnail.

## Step 5. Add the words locally (free)
Picture makers misspell. Words added on your own PC are sharp, spelled right and in your brand font.
- **Long video (16:9):** `thumb_finish.py <picture> <out.jpg> --text "1 EVENING" --font <your font file> --main "<colour>"
  --main2 "<colour>" --glow "<colour>" --edge "<colour>" --preview "<your title>" --others <your competitor folder>`
  - Its defaults are the kit's own house look (yellow letters, orange glow, Impact): pass your brand colours and font.
  - `--front mask.png` puts the hero in front of the letters (white = hero). `hero_mask.py` makes that mask for the
    kit's blocky hero only; for any other hero, cut it out with a free background remover and save a black-and-white mask.
  - `--darken`, `--light`, `--blur`/`--pixelate`, `--hue`, `--sat` and `--contrast` do the finishing touches.
  - The output is 1920 x 1080, above YouTube's minimum and above the 1280 x 720 its A/B tests need.
- **Shorts cover (9:16):** `thumb_vertical.py <picture> <out.jpg> --line1 "13 BILLION" --line2 "WHO?"` (1080 x 1920,
  also writes a phone-size copy).

## Step 6. The phone check, next to real competitors (free)
- `phone_view.py <your thumbnail> <competitor folder> <out.jpg> "<your title>"` draws two phone screens: the home feed
  (big, full width) and the up-next list (small). Add `titles.json` to the folder so their real titles show.
- `thumb_finish.py --preview` also makes a home-page grid with yours in the middle, plus a 160 px wide copy.
- Look at it at arm's length and answer: what do I see first? Can I read the words? Do I get the idea in one second?
  Would I click mine over the one above it? If any answer is no, fix it and check again.
- Ask **packaging-critic** for a score (its thumbnail points), and **hook-oracle** for a Shorts cover.

## Step 7. Upload and test (you do this in YouTube Studio)
- **Sizes (YouTube's current help page):** 16:9; recommended 3840 x 2160, at least 640 wide; JPG or PNG; up to 50 MB
  from a computer (2 MB from the phone app). Shorts: 9:16, recommended 2160 x 3840, at least 640 tall, and a custom
  Shorts thumbnail can only be added in YouTube Studio on a computer. Your account must be **verified** to upload your own.
- **A/B testing (long videos only):** in Studio, under the thumbnail, click **A/B Testing**, add up to 3 thumbnails.
  Needs advanced features. YouTube keeps the one with the most **watch time**. Not for Shorts. Details in **yt-titles**.
- **Rules:** YouTube removes misleading thumbnails (ones that suggest content not in the video), impersonation, sexual,
  violent or graphic images and vulgar words.

## Don't look like AI slop
**The tells:** waxy plastic skin, dead staring eyes, melted fingers, garbled letters and fake logos, the same purple-teal
haze and glow as everyone else, everything perfectly centred and shiny, details that mean nothing, a hero that looks
different in every video.

**The fixes:**
1. Describe the **idea**, not "epic, 8K, cinematic, masterpiece".
2. One light source plus a rim light, not glow everywhere.
3. Zoom to 100 % and check hands, faces, edges, letters and logos. Crop or remake anything broken.
4. No words from the picture maker: add them locally (step 5).
5. One look for the whole channel (brand sheet) and one character that never drifts (built in code, or one character
   sheet used as a reference every time).
6. One specific, true, slightly odd detail from your video.
7. Your own frame from your own video when you can.

An AI-made thumbnail is fine on YouTube: its AI-labelling page lists thumbnails as a "minor" use that needs no label.
What YouTube does not pay for is mass-produced, template-looking content with no original idea.

## How Claude helps
**Claude does:**
- writes the brief and 3 concepts, and scores them against the checklist;
- writes the picture prompt for the picture maker you chose (free or paid; it never presses Generate in a paid one);
- picks the clearest version at small size with you;
- adds the words locally in your brand colours and font, with the hero in front of the letters if you want;
- builds the phone check next to the competitors you saved, and asks the critics for an honest score;
- makes 2-3 versions for an A/B test, and notes the winner in the video's folder (`THUMBNAIL.md`).

**You decide:** the concept, which picture maker to use (and any spending), the final picture, the words (from 3-4
options shown on the picture), and the upload.

## Checklist
- [ ] One hero, one idea; the first thing the eye sees is the right thing.
- [ ] 0-3 words, adding to the title, never repeating it.
- [ ] Passes the cover-the-text test (both halves).
- [ ] Hero and words stand out in black and white; one accent colour.
- [ ] Rim light or glow separates the hero; text never covers the face or key object; bottom-right corner clear.
- [ ] Hands, faces, letters and edges checked at 100 %; no AI tells.
- [ ] Reads at feed size and up-next size next to real competitors.
- [ ] The video shows this scene within the first 5 seconds.
- [ ] Brand colours and font from `BRAND.md`.
- [ ] Size and file type fit YouTube's limits; account verified.

## Where this comes from
The kit's **thumbnail-design** (rule of thirds, palette, the 10 thumbnail types, local finishing, home-page test),
**packaging-method** and **packaging-critic** (cover-the-text test, text that adds, one first stop for the eye, mid-action,
the opening pays off the thumbnail), **sf-thumbnail** (one hero, 0-3 words added locally, rim light, phone check) and
**sf-niche-research** (the thumbnail is read first; test it beside real competitors).

## Sources (YouTube's own pages, checked 16 Nov 2026)
- Add custom thumbnails (sizes, file types, 50 MB, verified account, Shorts thumbnails on a computer):
  https://support.google.com/youtube/answer/72431
- Thumbnail & title tips (rule of thirds, easy-to-read font, not too busy, make it as large as possible):
  https://support.google.com/youtube/answer/12340300
- A/B test titles & thumbnails (up to 3, watch time, 1280 x 720 or larger, not for Shorts):
  https://support.google.com/youtube/answer/13861714
- Thumbnails policy (misleading thumbnails, impersonation): https://support.google.com/youtube/answer/9229980
- Disclosing use of GenAI content (thumbnails count as a minor use): https://support.google.com/youtube/answer/14328491
- Channel monetization policies (inauthentic, mass-produced content): https://support.google.com/youtube/answer/1311392
