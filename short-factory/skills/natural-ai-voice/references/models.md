# Voice models and settings (ElevenLabs, checked 29 Oct 2026)

| | eleven_multilingual_v2 | eleven_v3 | eleven_v4 |
|---|---|---|---|
| The studied creator's verdict | his choice for every video | "alpha": expressive but changed his voice's identity | not out when he made I03 (Jan 2026) |
| Audio tags `[excited]` | no (they are read aloud) | yes | yes |
| Pauses | `,` `...` and `<break time="0.6s" />` (max 3 s, a few per script) | `...`, `[short pause]`, `[pause]`, `[long pause]` | same as v3 |
| Stress | CAPS on one word | CAPS + tags | CAPS + tags |
| Sliders | stability, similarity_boost, style, speaker boost, speed 0.7-1.2 | stability, similarity | stability, similarity |
| Numbers | write as words | keep as written | keep as written |

## His v2 settings (from I03)
- **Speed:** a little up (he drags it right; use 1.05-1.10).
- **Stability: low** (≈0.30): more variation between takes, more emotion. Too low gets unstable; regenerate the bad batch.
- **Similarity: ≈70 %** (0.70): close to the voice without strain.
- **Style exaggeration: up** (≈0.40-0.50): more of the voice's own expressive style.
- Speaker boost on.

## v4 / v3 settings
- Stability ≈0.30-0.40 for varied takes (higher only if the voice drifts).
- Similarity ≈0.75-0.85.
- No speed slider: pace with `[slowly]`, `[quickly]`, `[pause]`, or fix speed in the edit (±8 %).
- A tag holds until the next tag: place one where the delivery changes, not on every sentence.
- Tags that work: emotion `[excited] [curious] [sarcastic] [surprised] [tired] [warmly] [nervous]`, delivery `[whispers] [softly] [dramatically] [deadpan] [mischievously]`, non-verbal `[laughs] [chuckles] [sighs] [exhales] [gasps] [clears throat]`, pauses `[short pause] [pause] [long pause]`, dialogue `[interrupting] [jumping in]`.
- Don't use stage directions (`[grinning]`, `[pacing]`); they aren't performed.

## The identity test (stage 2)
Same voice, same 2 lines, once on v2 with his settings and once on v4 with one tag. Play both next to the voice's preview. If v4 sounds like a different person, use v2 for the channel. Re-test when a new model version comes out.

Line pair for the test:
> So... you've been told the ocean is blue because it reflects the sky. [short pause] That's WRONG. Completely wrong!
