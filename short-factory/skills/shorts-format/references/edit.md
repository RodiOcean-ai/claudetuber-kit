# Edit, mix and final checks (Remotion, free)

## Project
- `<episodes_root>/<slug>/edit/`, a new Remotion project pinned to the installed version (same as ec-animatic). Never modify other Remotion projects.
- Composition: 1080×1920, 30 fps, duration = narration length + 0.3 s.
- One data file, `src/beats.ts`, holds `{id, clip|still, srcIn, start, end, exit: 'swipeL'|'swipeR'|'swipeU'|'swipeD'|'none'}` plus the Whisper word list `{w, s, e}`. Timing is changed only there.

## Picture
- Each beat starts on its first narration word (Whisper time) and ends where the next begins: no gaps, no black frames.
- **Swipe join (his signature):** over 3 frames, the outgoing clip slides 25 % of the width in the exit direction with a directional blur (CSS `filter: blur()` on an offset copy, or two offset copies at 50 % opacity), while the incoming clip slides in from the opposite side with the same blur. Add the whoosh sound on the middle frame.
- **Holds:** add a slow push (scale 1.00 → 1.05 over the beat) so the frame never freezes.
- **Lite stills:** split into a foreground and a background layer (a rembg-style cut-out, done locally), then a parallax push: background 1.00 → 1.03, foreground 1.00 → 1.08.
- **Loop:** the last 0.3 s must match frame one (same view). Check by putting the first and last frames side by side.
- No title card, no end card, no corner logo. The brand only appears on its prop.

## Captions
- Groups of 1-3 words from the Whisper words. Break at punctuation, and never leave a group longer than 0.9 s.
- Each group is visible from its first word's start to the next group's start.
- Style:
  - font Arial Black, or Montserrat ExtraBold if installed locally;
  - 64 px on a 1920 px-high frame, white;
  - 5 px black outline (stroke), with a soft shadow 0 3px 6px rgba(0,0,0,0.35);
  - centred, with the text's middle at 58 % of the frame height.
  Move it to 70 % only when the subject's face sits at 55-60 %.
- No word-by-word colour pop and no emoji in captions (he does neither).

## Sound
- **Narration** starts at frame 0 (trim any leading silence from the take). Target -14 LUFS for the narration alone, compressed to a loudness range of 4 LU or less (ffmpeg `acompressor=threshold=-20dB:ratio=4:attack=5:release=80`, then `loudnorm`).
- **Music:**
  - the whole length, 14-18 LU below the narration (for narration at -14 LUFS, the music sits at about -30);
  - 0.3 s fade-in at the start and 0.5 s fade-out at the end;
  - for a loop, cut the music on a bar line instead, so the replay does not jump.
- **Whooshes** at -24 to -20 LUFS (short), one per swipe. The impact at most once.
- **Master:** about -12 LUFS integrated, true peak -1 dBTP (`loudnorm=I=-12:TP=-1.5:LRA=5` on the final mix before encoding).

## Sharpen and export
- Before the final render, sharpen the 480p clips locally (4x-UltraSharp, frame by frame, back to 1080×1920; see ec-jingle-ad `references/studio-and-finish.md`). Check still frames for flicker.
- Render H.264, CRF 16, AAC 192 kbps, 1080×1920, 30 fps. Number the versions (`out/<slug>_v<N>.mp4`) and keep them all.
- Keep a Studio copy of the sound files if the owner wants a record inside ElevenLabs (optional; not a contest).

## Final checklist (run format_check.py, then eyeball)
- [ ] Voice on frame one, picture moving by 0.4 s, subject named in the first 3 words.
- [ ] 27-35 s, 75-95 words, 2.6-3.0 words/s, no pause over 0.5 s.
- [ ] 0-2 hard cuts; every scene change is a swipe or a fly-through.
- [ ] Music under the voice the whole time, 14-18 LU below; 2-5 sound effects.
- [ ] Captions 1-3 words, never over a face; no typos in the subject's name.
- [ ] The brand is on one prop only; no name of the benchmark channel anywhere; no copied mascot.
- [ ] Loop or big-picture ending; no outro.
- [ ] -12 LUFS, true peak -1 dBTP or lower; no black frames.
- [ ] Every fact matches `facts.md`.
