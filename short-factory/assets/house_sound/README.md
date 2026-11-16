# Sound library (bring your own)

`config.json` → `sound_library` points here. The skills say "use the house library first": put the music cues and sound
effects you are allowed to use in `music/` and `sfx/`, named by what they are, and keep a short list in this file.
The author's own library (paid ElevenLabs cues, Mixkit effects and sounds from earlier projects) is not included.

Free, safe sources:
- **Real instruments for Claude-composed music:** run `python -I scripts/get_instruments.py` once. It downloads two
  CC0 (public domain) sample libraries from the Versilian Studios projects on GitHub (about 740 MB) into `instruments/`;
  `scripts/house_sampler.py` then plays Claude's note lists with them. `instruments/tuning.json` and `octave_fix.json`
  (included) are the tuning tables for those recordings.
- **Sound effects:** Openverse or Freesound, CC0 preferred; credit CC BY sounds in your description; avoid BY-SA, NC and
  ND licences on a monetised channel.
- **Music:** the YouTube Audio Library, or your own.
