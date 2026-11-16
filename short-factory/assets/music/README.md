# Music beds (bring your own)

The edit rotates three background tracks named **sprint**, **clocks** and **steps** (one per Short, in turn). The kit ships
without the music files: use instrumental tracks you have the rights to use on YouTube (your own, a paid library, a free
library such as the YouTube Audio Library, or a generator whose terms allow it). You can also compose your own with
`scripts/house_sampler.py` after downloading the free instruments (see `assets/house_sound/README.md`).

For each track put two files here:
- `<name>.wav` - the track (about 40-60 s, ending on a clear final hit).
- `<name>.json` - its beat map. The three `.json` files here are examples of the format (they describe the author's tracks).

Ask Claude: "make the beat files for my music". It measures the beats with librosa; check the final hit by ear.
