---
name: natural-ai-voice
description: Make an ElevenLabs AI narration sound like a real person, with a measured method from our study of a fully AI-voiced 231k channel ("How I Actually Make AI Voice Sound Real", 722k views) - a unique designed voice, the right model and settings, a marked-up performance script (pauses, CAPS stress, "!" and "...", hesitations, v4 tags), generating 2-4 sentences at a time and keeping every take, then comping the best phrases from several takes, tightening pauses, speed and EQ, and measuring the result against the study's numbers; plus dubbing into other languages. Use whenever the owner asks for a voiceover, narration, AI voice, "make it sound human/real/less robotic", pauses, exaggeration, emphasis, dubbing, "comp the takes", "check the voice", or when a shorts-format or ad skill reaches its narration stage.
---

# Natural AI voice: an AI narration nobody notices

Learned from the studied creator's I03 (every word of that video is AI-voiced) and measured on all 9 of his videos (faceless-channel study of 29 Oct 2026; your own downloads in `<studies_root>/faceless-channel`, shipped notes in `${CLAUDE_PLUGIN_ROOT}/reference/creators/faceless-channel/`; numbers in `references/voice-data.md`).

**Rules:**
- **Claude builds, the owner clicks.** Claude marks up the script, builds nodes or a paste-ready text, and prices with `estimate_only`. The owner presses Generate (board or Text to Speech page). Never run a generation.
- **Never clone anyone else's voice,** and never imitate the studied creator's voice or his narrator's style of jokes. Our voice is designed by us, or is the owner's own clone.
- Plain English to the owner; one stage at a time.

## Why AI voices sound fake (the study's 4 elements)
A real voice has: 1. **tone that goes up and down** (monotone = robot), 2. **pauses on the important points** (not everywhere), 3. **stressed key words**, 4. **a human-written script**. The 4th comes from **story-scripts** (run its human-writing pass first). And even with all four, one long generation follows a pattern listeners eventually feel. His fix for that is the core of this skill: **many short takes, comped together**. The proof is in his own numbers: his 2023 videos swing only 0.4 semitones in tone between phrases (nearly flat); since 2024 they swing about 2.0, five times more, and the speed varies twice as much (`references/voice-data.md`).

## Stage 1. The voice (once per channel)
- **Design a unique voice** (Voice Design in the app; the connector can't create voices). Nobody else can use it, which makes it a brand. Describe age, accent, persona and **"speaks with a lot of emotion, quirky but charismatic"**-type energy; lower the guidance a little to let it surprise you; try several previews.
- Or **clone the owner's own voice** (Instant Voice Clone from a clean sample; Professional needs 30+ min). Only the owner's own voice.
- "You're married to it": the same voice for every video. Save its ID in the project (`channel_voice.txt`).
- Templates: `references/voice-design.md` (an explainer narrator, a storyteller, a mentor second voice).

## Stage 2. Model and settings — read `references/models.md`
**Do the identity test first (≈200 credits, owner presses Generate):** the same 2 lines on `eleven_v4` and on `eleven_multilingual_v2`. The studied creator rejected v3 in its alpha because it **changed the voice itself** ("my evil twin"). If v4 keeps the voice, use v4 (tags give the most control); if it drifts, use v2.
- **eleven_multilingual_v2 (his choice):** speed 1.05-1.10, **stability low** (≈0.30), **similarity ≈0.70**, **style exaggeration up** (≈0.45), speaker boost on.
- **eleven_v4 (or v3):** stability ≈0.30-0.40 (varied takes), similarity ≈0.75-0.85; mood and pace come from tags, not sliders (no speed slider).

## Stage 3. Mark up the performance script (free)
Rewrite the final script as `voice_script.txt`, split into **batches of 2-4 sentences** (numbered `B01`, `B02`...). In each batch:
- **Stress:** ONE key word in CAPS per sentence at most ("this is the ONLY way").
- **Excitement:** "!" (more than one if it under-reacts). **Doubt, disappointment, trailing off:** "...".
- **Pauses:** a comma or "..." inside the text; on v2 a `<break time="0.6s" />` for an exact pause (a few per script at most); on v4 `[short pause]` / `[pause]`.
- **Tone swings (v4):** a tag where the delivery CHANGES, not on every line: `[excited]`, `[sarcastic]`, `[curious]`, `[whispers]`, `[sighs]`, `[laughs]`, `[deadpan]`. Describe how it's said, not actions.
- **Human noise, written in:** a hesitation ("So... no, wait."), a self-correction, a filler ("I mean", "look", "okay so"). The studied narration has about 6 such words a minute; we aim for 2-6. One "um" or "uh" per minute at most, on v4 only (v2 often reads it badly).
- Numbers as words on v2; as written on v4.
Show the owner 2 marked batches before marking the rest. **Best of all, have the owner read the marked script once in Transcript Recorder** and copy his natural pauses, slow-downs and stresses into the tags (`references/owner-read-lessons.md`). Examples: `references/markup-examples.md`.

## Stage 4. Generate in small batches (owner clicks; price first)
- **Where:** the **Text to Speech page** is best for this: after each generation, regenerating the same text is free twice (his "two extra regenerations for free"; check it's still true on the page), so every batch gives 3 takes for one price. A board needs one node per take; price both and show the owner.
- **Per batch:** generate, keep **all** takes, download them. If a batch is wrong, regenerate only that batch (cheap).
- **Naming:** `B03_t1.mp3`, `B03_t2.mp3`, `B03_t3.mp3` in `voice\takes\`.
- **Cost:** roughly 1 credit per character per generation on the multilingual/v3/v4 models; a 1,500-word script ≈ 9,000 characters. Comping usually needs 1-3 generations per batch: estimate 10,000-25,000 credits for a 10-minute script, 300-800 for a 30-second short. Always replace with real `estimate_only` numbers before asking.

## Stage 5. Comp: the secret (free, local)
"Each time you hit generate, the tone changes slightly." Mixing takes gives the natural variation one take can't.
1. Run `short-factory\scripts\voice_comp.py <takes folder> <voice_script.txt>`: it transcribes every take, lines them up word by word against the script, flags misreads, and scores each phrase for life (pitch swing, stress, speed) with `voice_style.py`.
2. It proposes a **comp list**: for each sentence, which take, or which phrase from which take ("B03: t2 up to 'chop some parts', then t1 to the end"), cutting only at word gaps.
3. The owner listens to the proposal (it renders `voice\comp_draft.wav`) and swaps any choice by ear. Final say is the owner's ear.

## Stage 6. Tighten (free, local; `voice_comp.py --finish`)
- **Cut the dead air between sentences** to 0.08-0.20 s (he starts the next line right after the last ends), BUT
- **keep deliberate pauses** of 0.5-1.2 s before a reveal, after a punchline and on the key points (marked `||` in `voice_script.txt`). His videos keep about 2-3 pauses over 1 s per minute; everything else is tight.
- **Speed:** if the whole read is too slow or fast, change it with pitch kept (rubberband/atempo), at most ±8 %.
- **Clean-up chain (his EQ step):** high-pass at 80 Hz, a gentle cut in the boxy/echoey area (250-450 Hz, find the exact spot by ear), light presence lift at 3-5 kHz, de-ess, compressor, loudness -14 LUFS for the voice alone.

## Stage 7. Check (free)
`python -I short-factory\scripts\voice_check.py <final_voice.wav> natural|format` compares the narration with the measured targets (`references/voice-data.md`) and prints YES/NO for: tone swing between phrases, speed variation between phrases, stressed words per minute, deliberate pauses per minute, dead-air gaps, fillers, overall speed. Fix every NO (usually: re-comp from livelier takes, or regenerate the flattest batches with more marks).

## Modes
- **natural (long talk-to-camera narration, tutorials, stories):** fast and lively: 3.4-4.0 words a second inside phrases, phrase speed varying 15 %+ , tight joins, 1-3 deliberate long pauses a minute, 2-6 conversational words a minute.
- **format (shorts-format, what-if-longs):** keep the format benchmark's even, brisk 2.6-3.0 words a second and almost no pauses in shorts, but still use **batches + comping + CAPS stress** for life. Longs: deliberate pauses only where the edit has a music drop or black beat. Fillers off (the format benchmark uses none).
- **format-real (every Short since 12 Nov 2026, owner: "we lose the tone battle, [the format benchmark] always wins"):** measured on the format benchmark's 10 top Shorts against our 8 voices, its narrator speaks in 14-25-word sentences (ours were 5-11), stops about 10 times a minute (ours 16-26), never pauses half a second, stresses half as many words and keeps loudness within about 1 dB. So: flowing sentences in the script, the WHOLE script in ONE node, one calm mood with at most two extra tags where the model Short's delivery changes ([curious] on the "But" line, [thoughtful] on the example), **no batches, no comping, no CAPS**, 2-3 takes, finish = one fixed volume and nothing else. Check with `voice_check.py <wav> format-real`; the older "format" targets were the format benchmark's pace with natural-level life and passed voices that still sounded like adverts.
- **ad / jingle voices:** use ec-acting for character voices; this skill's comping still applies.

## Stage 8 (bonus). Dubbing: his "real superpower" of AI voice
1. Export two audio files from the finished edit: **voice only**, and **music + effects only**.
2. ElevenLabs **Dubbing** (owner presses Generate; price first): source language, target language, upload the voice-only file.
3. Line the dubbed voice up against the original voice (as the timing guide) over the music + effects track; apply the same clean-up chain; export audio only.
4. YouTube Studio → Languages → the video → add the language → **upload the audio track** (delete YouTube's automatic dub of that language first). Translate the title and description too.
5. Start with Spanish, Hindi and Portuguese (his picks; half of YouTube's audience is in the top six languages and only about 20 % speaks English). Check "views by audio track" in Analytics after 28 days.

## Reference files
- `references/voice-data.md`: measured numbers per video and the targets for each mode.
- `references/models.md`: the v2 / v3 / v4 differences, settings and tags.
- `references/voice-design.md`: Voice Design templates.
- `references/markup-examples.md`: before/after marked batches (explainer, story, format mode).
- Tools in the plugin's `scripts` folder (`short-factory\scripts`): `voice_style.py` (measure any voice), `voice_comp.py` (comp the takes), `voice_check.py` (pass/fail against the targets).

Source: our own analysis of public videos from Isaac (@isaacverse). Not affiliated with or endorsed by Isaac or @isaacverse.
