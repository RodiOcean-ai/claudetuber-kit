# Voice and music (bring your own)

Every style plays two files from here: `voice.wav` (the 15-second narration) and `music.wav` (the music bed, about 15 s,
set about 15 LU under the voice). They are not included (the author's channel voice and paid music). Make the voice
with a free local model (see the explainer-styles skill: Chatterbox, then ClearerVoice) or record it yourself; if your
narration's timing differs, rebuild `src/shared/words.json` and `phrases.json` with `tools/words.py` and
`tools/timing.py` so every style follows the new word times.
