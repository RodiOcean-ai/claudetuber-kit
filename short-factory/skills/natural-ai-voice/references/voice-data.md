# Voice numbers (measured 29 Oct 2026 with `voice_style.py` on the separated voice track)

| # | Year | Words/s inside phrases | Phrase speed variation | Tone swing between phrases (semitones) | Stressed words/min | Pauses over 1 s per min | Pauses 0.5-1 s per min | Conversational words/min |
|---|---|---|---|---|---|---|---|---|
| I01 Thumbnails | 2024 | 3.71 | 18 % | 1.97 | 24 | 2.6 | 0.8 | 6.4 |
| I02 Editing | 2025 | 3.89 | 21 % | 1.78 | 25 | 2.1 | 1.6 | 6.0 |
| I03 AI voice | 2026 | 3.43 | 24 % | 2.14 | 27 | 2.1 | 2.4 | 8.5 |
| I04 Shorts 7 days | 2026 | 3.13 | 29 % | 3.16 | 17 | 3.3 | 1.7 | 6.4 |
| I05 Shorts 365 days | **2023** | 3.76 | 15 % | **0.38** | 24 | 1.6 | 1.0 | 4.5 |
| I06 Broke YouTube | **2023** | 3.84 | 11 % | **0.46** | 23 | 0.3 | 1.7 | 4.6 |
| I07 Scripts | 2026 | 3.58 | 23 % | 1.39 | 22 | 1.9 | 1.9 | 6.6 |
| I08 AI video | 2024 | 3.77 | 23 % | 1.74 | 21 | 1.9 | 1.8 | 6.1 |
| I09 Channel | 2026 | 3.56 | 22 % | 2.27 | 17 | 1.7 | 2.9 | 8.3 |
| **Median 2024-26** | | **3.58** | **23 %** | **1.97** | **22** | **2.1** | **1.8** | **6.4** |
| Format benchmark shorts (median) | | 3.04 | 11 % | 1.60 | 22 | 0.0 | 0.0 | 3.1 |
| Format benchmark longs (median) | | 2.78 | 20 % | 2.40 | 24 | 0.4 | 2.2 | 2.2 |

## What it shows
- **His method works, and you can hear it in the numbers.** His 2023 videos (one long generation, before the batch-and-comp method) have a tone swing of about 0.4 semitones between phrases: nearly flat. From 2024 on it's 1.4-3.2 (about 5 times more), and the speed varies twice as much (11-15 % → 18-29 %). That's the difference between "robot" and "is this a person?".
- **He is fast:** about 3.6 words a second inside phrases (around 215 words a minute), 3.0-3.2 overall with pauses. The joins between sentences are cut tight; the real pauses are deliberate (about 2 a minute over 1 s).
- **Stress:** about 22 clearly stressed words a minute (one every ~10 words), the same as the format benchmark. Stress isn't the difference; tone and speed variation are.
- **Conversational words:** about 6 a minute ("so", "like", "right", "well", "look", "I mean", "okay", "wait", "dude"). The counter includes ordinary uses of "so" and "like", so read it as a rough guide.
- Sentences average about 10 words, with lengths spread widely (from 1 word to 40).
- His voice sits at about 125 Hz (a baritone-ish young male).

## Targets used by `voice_check.py` (`short-factory\scripts\voice_targets.json`)
- **natural:** 3.2-4.0 words/s; phrase speed variation 17-30 %; tone swing 1.4-3.2; stressed 16-28 a minute; pauses over 1 s 1.5-3.5 a minute; 0.5-1 s 0.8-3.0; conversational words 4-9.
- **format:** the format benchmark's pace (2.7-3.3 words/s) and no pauses, but natural-level life (tone swing 1.3+).
- **format-long:** 2.5-3.2 words/s; holds only at music drops.

## Mix numbers (his finished videos)
- Mix about **-18 LUFS** (quiet for YouTube, which plays at up to -14) and his true peaks go over 0 dB (clipping). Don't copy that: we master to -14 LUFS, -1 dBTP.
- Voice about **9 LU above the music** (5.6-12.2); the format benchmark's shorts are about 16. Music under the voice about 90 % of the time.
