---
name: yt-branding
description: Set up a faceless YouTube channel's brand once and keep it in one small brand sheet that every other kit skill reads (short-factory/assets/brand/BRAND.md) - channel name and @handle check, a logo / profile picture that reads at 98 px in a circle, the banner with YouTube's current sizes and safe area, 2-3 brand colours plus one accent with contrast rules, one or two fonts, a mascot or host built in code so it never drifts, and the channel VOICE (design one voice once and keep it; free local options vs paid; never copy a real person's voice; licence check for a monetised channel). Use when the person says "brand my channel", "channel name", "handle", "logo", "profile picture", "banner", "channel art", "brand colours", "which font", "mascot", "channel voice", "brand sheet", "BRAND.md", or when starting a new channel.
---

# Your channel brand: decide once, write it down, use it every time

**For Claude:** plain English, one question per message, show pictures rather than describe them. Never sign in,
never upload, never spend: the person changes the channel in YouTube Studio and pays for anything paid.
Never install anything without asking first (name, source, size).

## The one idea
A faceless channel is recognised by its **colours, font, character and voice** before anyone reads the name.
Decide them once, write them in **one brand sheet**, and every video, thumbnail and banner uses the same sheet.
A look that changes every week is no brand at all.

## The brand sheet: where it lives and what's in it
**File:** `short-factory/assets/brand/BRAND.md`. The brand's pictures sit next to it in `short-factory/assets/brand/`
(`logo_800.png`, `banner_2560x1440.png`, `watermark_150.png`, your font files in `fonts/` with their licence files).
If the guided start (**start-claudetube**) is in use, write this file's place into its progress file (`brand_sheet`).

**Format:** a Markdown file with one block of `key: value` lines (YAML) that the skills read, then a few lines of notes.
Only you change it; Claude proposes changes and dates them.

```yaml
channel_name: "Tiny Body Lab"
handle: "@tinybodylab"
niche_sentence: "I make 60-second animated explainers about the body in emergencies for nurses and students."
audience: "nursing students and new nurses, 18-30"
edge: "15 years on an emergency ward"
first_ideas: ["What happens in your body when you faint?", "Why CPR breaks ribs", "The 4 minutes after a bee sting"]
title_pattern: "question + one emoji (Shorts); How to / Why + (Full Guide) (long)"   # or "none yet"
colours:
  base: "#0E1B2C"     # background, about 60 %
  main: "#F4F1EA"     # text and shapes, about 30 %
  second: "#3FA7D6"   # optional
  accent: "#FF5A36"   # about 10 %, only on the one thing that matters
contrast_checked: "main on base 15.4:1; accent on base 5.6:1; second on base 6.4:1"
fonts:
  headline: "fonts/Anton-Regular.ttf (SIL Open Font License)"
  body: "fonts/Inter-Bold.ttf (SIL Open Font License)"
thumbnail_text: "1-3 words, headline font, main colour, accent glow"
logo: "logo_800.png"
banner: "banner_2560x1440.png"
watermark: "watermark_150.png"          # or "none"
mascot: "Dot: a round cyan cell with one big eye; code: <file>"   # or "none"
voice:
  kind: "own voice"                     # own voice | own voice, cloned locally | designed voice | preset voice
  engine: "USB mic"                     # e.g. Chatterbox, Qwen3-TTS, Kokoro, a paid service
  sample: "voice/reference_10s.wav"     # the reference sentence every new read is compared with
  settings: "calm, warm, 2.8 words a second"
  licence: "my own voice"               # or the model's licence tag, or the paid plan that includes commercial use
never: ["real people's faces or voices", "red-green as the only difference", "more than one accent colour"]
updated: "2026-11-16"
```
**Who reads it:** **yt-niche** (the niche lines), **yt-titles** (the title pattern), **yt-thumbnails**,
**thumbnail-design** and **sf-thumbnail** (colours, fonts, text style, mascot) and **sf-edit** (the brand in the edit).
**For Claude:** also take the colours, fonts and mascot from here when running **explainer-styles** and its style
skills, and the voice card when running **natural-ai-voice** or the free local voice.

## 1. Name and @handle
- **Good names:** 1-3 words, easy to say and spell after hearing it once, hints at the promise or has a hook, not the
  name of a real company or person. Read it aloud to someone: can they type it?
- **Check it's free:** search the name and the handle on YouTube, and the same handle on the other apps you'll post to.
  The real check is YouTube Studio itself (Customisation, then Profile): it says at once if a handle is taken.
- **YouTube's handle rules:** 3-30 characters; letters or numbers; `_` `-` `.` allowed but not at the start or end; not
  case-sensitive; must not look like a web address or a phone number; one handle per channel.
- **Changing later:** the name and the handle can each be changed twice in 14 days. An old handle is held for you for
  14 days, then anyone can take it. Changing the channel name removes a verification badge. So choose with care.

## 2. Logo and profile picture
- YouTube shows the profile picture at **98 x 98 px**, and in most places as a circle. JPG, GIF (not animated), BMP or
  PNG, up to 15 MB. Make it square and large (we use 800 x 800 px); YouTube shrinks it.
- **What reads that small:** one bold shape, one or two letters, or the mascot's head. Brand colours. No thin lines,
  no small words, nothing important near the corners (the circle cuts them off).
- **The tests:** shrink it to 98 px and to about 36 px, in a circle, on a white page and a dark page. Can you still tell
  what it is? Does it look like nobody else's?
- **How to make it:** Claude can draw a simple logo in code (SVG, an exact-colour vector picture) and export the PNG,
  for free. Or Claude writes a prompt for the picture maker you choose and you run it.

## 3. Banner (channel art)
YouTube's sizes:
- upload **at least 2048 x 1152 px** (16:9); **2560 x 1440 px recommended** (especially for TV); **6 MB or smaller**;
- the **safe area** for text and logos is **1235 x 338 px** in the middle (at the 2048 size). Everything outside it can
  be cut off on phones and computers;
- no shadows, borders or frames around the picture.
**Our recipe:** design at 2560 x 1440 and keep all words and the logo inside the centre **1544 x 423 px** (the same safe
area, scaled up by 1.25). Put in it: the channel promise in 6 words or fewer, and, if you keep to it, the rhythm
("New animated explainer every Tuesday"). Fill the rest with the brand colours and the mascot or a scene from your style.
Claude builds it locally with the safe area drawn as a guide layer, shows you the phone, computer and TV crops, then
exports a clean copy.

**Watermark (optional):** a square picture, at least 150 x 150 px, under 1 MB, shown at the end of the video (last 15
seconds), from a time you choose, or the whole video. Not available on made-for-kids videos.

## 4. Colours: 2-3 plus one accent
- **Base** (the background colour), **main** (text and shapes), an optional **second**, and **one accent** used only
  on the thing you want seen first (the thumbnail word, the key number, the mascot's eye).
- **A rough split:** base 60 %, main 30 %, accent 10 %. If the accent is everywhere, it stops working.
- **Contrast rules** (from the web's accessibility standard, WCAG): at least **4.5 : 1** between small text and its
  background (captions, labels), at least **3 : 1** for large bold text and shapes (thumbnail words, titles, icons).
  Claude measures every pair and writes the numbers in the sheet.
- **Black-and-white test:** turn the thumbnail grey. If the hero and the words disappear, the colours only differ in
  hue: make one lighter or darker.
- **Never red against green** as the only difference (many viewers can't tell them apart).
- Check the accent on YouTube's white page **and** its dark page.

## 5. Fonts: one or two
- **One headline font:** bold, thick, readable at thumbnail size (for example Anton, Bebas Neue, Montserrat Black).
- **One body font** for captions and labels (for example Inter, Roboto, Montserrat).
- **Licence:** fonts from Google Fonts may be used commercially, also in videos and logos; each font's own licence
  (most often the SIL Open Font License) sets the terms. Keep the licence file next to the font in `assets/brand/fonts/`.
- The kit's thumbnail scripts default to the kit's house font (Impact): pass your font with `--font`.

## 6. Mascot or host (optional)
- Faceless doesn't mean characterless. A recurring character makes viewers feel they know the channel.
- **Build it in code, not from picture prompts.** A puppet made of shapes in Remotion (**explainer-2d-character**) or a
  blocky figure in Blender (**sf-blocky-world**) keeps the same proportions, colours and face in every video. A
  picture maker redraws the character each time, and it drifts.
- Give it: one clear outline shape, one main colour from the brand, one prop or accessory, and maybe one habit
  (a running gag it does once a video).
- For thumbnails from a picture maker: render one character sheet from the code-built character (front, side, back,
  three faces) and use it as the reference every time.
- Never a real person's face or likeness, and never another channel's mascot.

## 7. The voice: design it once, keep it
On a faceless channel the voice is the face. Pick one, write it down, use it on every video.

| Option | Cost | Good to know |
|---|---|---|
| **Your own voice** (any USB mic) | free | the most human and the most yours; no licence questions |
| **Your voice, cloned on your own PC** | free | Chatterbox (MIT licence; copies a voice from a short sample; marks its audio with a hidden watermark; the kit's `voice_make.py` uses it, see `assets/voice/README.md`) or Qwen3-TTS Base (Apache 2.0; clones from about 3 s of audio) |
| **A voice designed from a description, on your PC** | free | Qwen3-TTS VoiceDesign (Apache 2.0) builds a voice from a text description; runs best on a graphics card |
| **A preset voice on your PC** | free | Kokoro (Apache 2.0, 54 preset voices, no cloning): easy, but others can use the same voice |
| **A paid voice service** (for example ElevenLabs Voice Design) | paid | a designed voice only you use. On ElevenLabs the free plan has no commercial licence; Starter is the first plan with one (and with instant voice cloning) |

**Rules:**
- **Never clone or imitate a real person's voice** without their clear written permission: not a celebrity, not
  another creator, not a friend "for fun". YouTube asks you to label realistic content that makes a real person seem
  to say something they didn't. Cloning **your own** voice for voice-overs and dubs needs no label.
- **Licence check before a monetised channel uses it:** open the model's own page and read its licence tag. MIT and
  Apache 2.0 allow paid use. Anything marked non-commercial ("NC"), "research only" or a custom licence: not for a paid
  channel until you have read it. For a paid service: your plan must include a commercial licence.
- **Write a voice card** in the sheet: kind, engine, settings, licence, and a 10-second reference recording. Compare
  every new video's voice with it (the kit's `voice_style.py` measures pitch movement and speed).
- **Change it only if it's broken,** and then everywhere at once.
- Making it sound human: **natural-ai-voice** (paid voices) and the free voice steps in **explainer-styles**.

## How Claude helps
**Claude does:**
- writes 10 name ideas with handle versions, checks them against YouTube's rules and searches for clashes;
- draws the logo in code, or writes the picture prompt; tests it at 98 px and 36 px in a circle, light and dark;
- builds the banner at 2560 x 1440 with the safe area marked, shows the crops, exports a clean copy;
- proposes 3 colour sets, measures every contrast pair, runs the black-and-white test;
- suggests font pairs and checks their licences;
- designs the mascot's parts and builds it in code with the style skills;
- sets up a free local voice (asking before every install), or writes a voice design prompt for the service you choose,
  and checks the licence on the model's own page;
- writes and updates `BRAND.md` and dates every change.

**You decide:** the name and handle, the look (from options Claude shows as pictures), the voice (by ear), anything that
costs money, and every change in YouTube Studio (you upload the logo, banner and watermark yourself).

## Checklist
- [ ] Name says the promise or has a hook, and is easy to say and spell.
- [ ] Handle fits the rules and is free on YouTube (checked in Studio) and on your other apps.
- [ ] Profile picture reads at 98 px and 36 px in a circle, on light and dark.
- [ ] Banner 2560 x 1440, 6 MB or less, words and logo inside the centre 1544 x 423 px; crops checked.
- [ ] 2-3 colours plus one accent; contrast at least 4.5 : 1 (small text) and 3 : 1 (big text); grey test passed.
- [ ] One headline font and one body font, licences saved.
- [ ] Mascot (if any) built in code, with a character sheet for thumbnails.
- [ ] One voice: kind, engine, settings, licence and a reference recording written down; no real person copied.
- [ ] `short-factory/assets/brand/BRAND.md` saved and dated.

## Where this comes from
The kit's **thumbnail-design** (a 5-colour palette with one changing highlight, one uncommon font), **channel-playbook**
(brand from day one: name, one font, a palette, one art style, a mascot of your own), **explainer-2d-character** and
**sf-blocky-world** (characters built in code), **natural-ai-voice** and `assets/voice/README.md` (one voice, never
someone else's), and the kit's checks of free voice-model licences on their own pages.

## Sources (checked 16 Nov 2026)
- Manage your channel branding (profile picture 98 x 98 px and 15 MB; banner 2048 x 1152 minimum, 1235 x 338 safe area,
  2560 x 1440 recommended, 6 MB; watermark 150 x 150, under 1 MB): https://support.google.com/youtube/answer/10456525
- Learn about YouTube handles (3-30 characters, allowed characters): https://support.google.com/youtube/answer/11585688
- Change, view, or hide your handle (twice in 14 days, old handle held 14 days): https://support.google.com/youtube/answer/15920820
- Manage your channel's profile (name twice in 14 days, badge removed): https://support.google.com/youtube/answer/2657964
- Disclosing use of GenAI content (real people; your own cloned voice is a minor use):
  https://support.google.com/youtube/answer/14328491
- WCAG 2.1 contrast minimum (4.5 : 1 and 3 : 1): https://www.w3.org/TR/WCAG21/#contrast-minimum
- Google Fonts FAQ (commercial use, licences): https://developers.google.com/fonts/faq
- Voice model licences, on each model's own page: https://huggingface.co/ResembleAI/chatterbox (MIT),
  https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base (Apache 2.0),
  https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign (Apache 2.0), https://huggingface.co/hexgrad/Kokoro-82M (Apache 2.0)
- ElevenLabs plans (commercial licence from Starter): https://elevenlabs.io/pricing
