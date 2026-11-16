# Prompts (copy, then fill the [brackets])

Never write the benchmark channel's name, "Pixar" or any studio or creator name in a prompt. Describe the look instead.

## Voice: the channel narrator (the owner designs it once in the ElevenLabs app)
Voice Design description:
> Native English, General American. Male, late 20s to early 30s. Studio quality, close microphone, dry room, no reverb. Persona: a friendly science explainer telling a friend something fascinating; calm, curious and matter-of-fact, never dramatic or salesy. Emotion: lightly intrigued. Timbre: clear, bright mid-range, slightly soft consonants. Pacing: brisk and very even, about 170 words per minute, with no long pauses.

Sample line for the previews: "If you get a splinter, most people just pull it out. But sometimes it goes so deep that your body has to push it out for you."

Save the chosen voice's ID in `<studies_root>/shorts-format/channel_voice.txt` and reuse it for every short and long video.

## Narration (Eleven v4, or v3 if v4 is unavailable; natural-ai-voice, format mode)
- Split the script into 2-3 batches of 2-3 sentences. Put a single `[curious]` tag at the start of batch 1 only.
- Commas and full stops only: no "…", no dashes, no `||` holds. Those create pauses he never makes.
- CAPS on at most ONE word per batch, for stress (natural-ai-voice); stress adds life without adding pauses.
- Write numbers the way they are said ("two to four times", "eighty-two billion").
- Invented or hard words: respell them so they're heard right, and check by ear.
- 3 takes per batch (1 paid + 2 free regenerations on the Text to Speech page), then comp with `short-factory\scripts\voice_comp.py`. If the comp runs over 36 s, cut words rather than speeding it up (speed at most 1.08x).

## Look block (put it at the end of every image and video prompt)
> Semi-realistic 3D animation, smooth stylised surfaces, soft global illumination, gentle daylight, clean saturated colours, very shallow clutter: one subject isolated in the centre of a clean, empty set with a soft pale-blue sky gradient behind it (or a white-blue studio floor). Characters have smooth skin, no pores, no wrinkles, friendly realistic proportions. Crisp focus on the subject, soft background. Vertical 9:16 composition, subject in the middle third, empty space above and below for captions. No text, no logos, no watermark, except [BRAND] where stated.

Body cutaway add-on:
> Medical cutaway style: the skin peels open into a clean cross-section, bright red muscle fibres, blue and red blood vessels, yellow fat lobules, glowing particles for cells, simple white arrows for forces.

Scale add-on:
> Scale comparison: the [thing] laid beside a familiar landmark ([football field / Central Park / a city skyline / the whole Earth]) seen from above, clean map-like colours.

## Keyframe (gpt-image-2.5-sunburst, medium, 2K, 9:16)
> Vertical 9:16 start frame of a short animated explainer. [WHO/WHAT, one subject] is [ALREADY mid-action: the first moment of the beat]. Camera: [close / medium / wide], [angle], subject centred. Setting: [minimal set]. [BRAND RULE if this beat carries the prop: The [prop] has "[BRAND]" printed on it in plain bold letters, lying naturally on its surface, verbatim, no extra characters.] [LOOK BLOCK]

Character sheet (only for a person in 2+ beats): one picture, three panels (body without a head, head front, head side profile), the look block, plain light-blue background.

## Video beat (Seedance 2.5, 480p, 9:16, audio off, start frame = keyframe)
> One continuous shot, the camera never stops moving. [0-1 s]: [what moves immediately — motion in the first half second]. [1-N s]: the camera [pushes in / flies along / dives into the cross-section / orbits / rises with] [subject] as [action, step by step, matching the narration words]. Final 0.4 s: the camera whips fast [left/right/up/down] with heavy motion blur. Consistent character and objects throughout, no deformation, no extra limbs, no text appearing, no cuts. [LOOK BLOCK, short form]

- Loop beat: also set the end frame to beat 1's keyframe, and write "the camera pulls back and settles exactly on the opening view".
- Slow motion for impacts: "in slow motion, 4× slower, the bullet visibly travels".
- Inside the body: "the camera dives through the skin surface into the cross-section in one move".
- Never ask for spoken words or sound. Audio off.

## Lite-mode still (for beats that are not video)
Same keyframe prompt, but compose it with a clear foreground and background, so the edit can split it into 2 layers for parallax: "foreground subject clearly separated from a soft background".

## Music bed (Eleven Music v2.5, instrumental, 35 s)
> Light, curious documentary underscore: soft marimba and plucked strings over a gentle synth pad, steady 108 BPM, warm and inquisitive, even energy from start to end, no vocals, no drums build-up, no drop, no big ending, loops cleanly.

Alternatives by mood:
- war or history: "soft pizzicato strings and low brushed percussion, steady and curious";
- gross or scary: "light, playful-creepy music box and pizzicato".
Keep it even: shorts have no music drops.

## Sound effects (eleven_text_to_sound_v2, 1-2 s each)
- Whoosh: "fast soft air whoosh, smooth, close, no tail, 0.6 seconds".
- Impact: "single muffled thud, small and clean, no echo".
- Body squelch (sparingly): "tiny soft wet squish, subtle".
- Pop or fizz: "small bottle cap pop then quick fizz".
