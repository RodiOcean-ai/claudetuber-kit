# The benchmark's top 100 scripts: the measured script rules (study of 12 Nov 2026)

The scripts of his **100 most-viewed Shorts** (71M-255M views each), transcribed locally (faster-whisper medium.en; the stitches Short from the older large-v3-turbo transcript), split into sentences at the narrator's full stops and counted. Story type and ending type are Claude's reading of each script. Speech-to-text can mishear a word, so single counts are close, not exact.

- Data (plugin): `reference/creators/shorts-format/top100/`
  - `library.json`: one row per Short: rank, id, title, views (M), seconds, words, sentences, story type (`spine`), opener, first "But" second, ending, first word of every sentence (`glue`).
  - `scripts.json` (every sentence with its start and end time) is not included in this kit: it holds the transcribed words. Measure your own model Short instead (see sf-pipeline).
  - `stats.json`, `stats2.json`: the raw counts below. `labels.json`: story type and ending per rank.
- Raw audio and transcripts: `<studies_root>/shorts-format/top100`.
- The owner's course built from this study: a script course (a private page, not included) (lessons, drills, a script checker, the sortable library).

**What we copy is the shape, never his words or topics.** Never paste his sentences into our scripts or onto public pages.

## 1. The box (100 Shorts)
| Measure | Median | Middle half | Note |
|---|---|---|---|
| Length | 29 s | 26.5-33 s | fables run about 60 s |
| Words | 81 | 72-91 | |
| Sentences | 5 | 4-6 | |
| Words per sentence | 15 | 80 % fall in 8-24 | only 2.5 % under 6 words; 18 % over 20 |
| Speaking speed | 2.8 words/s | 2.6-2.9 | |
| Pauses over 0.5 s | 0 | | |
| "Subscribe", "follow", intro, outro | 0 of 100 | | |
| Talk about himself or his opinion | 3 of 100 | | never "guys", "crazy", "insane" |
| Numbers | none in at least 58 of 100 | | only a number-is-the-topic Short uses several |
| "You" anywhere | 78 of 100 | median 2 per script | |

**No dramatic fragments.** "X. Y. Z." triplets and 2-4-word sentences are not his style (2.5 % of his sentences). Where the faceless-channel study's "mix sentence lengths" advice (story-scripts) would add fragments, the measured shorts-format rule wins for Shorts.

## 2. Line one (how the 100 first sentences start)
| Opener | Shorts |
|---|---|
| "If…" (almost all "If you…") | 35 |
| Cold open, a person mid-action ("He took…", "They opened…") | 19 |
| "When…" / "As…" | 17 |
| Cold open, a thing mid-action ("The bullet was shot…") | 10 |
| A question to the viewer ("Have you ever…", "Do you notice…", "You know…") | 8 |
| Fact first | 4 |
| Command ("Place the flies…") | 3 |
| "Imagine…" | 2 |
| Wrong belief first ("Most people think…", "You might think…") | 2 |

So the "you" opener is the default, but a **cold open mid-action is a full second form (29 of 100)**, mainly for true stories and processes. Do not mark a cold open down on a true-story or process script. The hook sentence often carries the wrong belief too ("If you…, you might think…"), so the "But" can come early.

## 3. The glue words
Of the 464 sentences after a first line:
- **59 %** open with a glue word, **26 %** point back at what was just shown ("This…", "He…", "The bullet…", "Inside…"), only **15 %** start cold.
- In more than half of the scripts, every sentence after the first is glued or points back.

What the later sentences start with: **And 69 · But 62** · He/She/They/It 46 · This/These/That 38 · The/A + thing 28 · **Now 23 · You see 18 · Then 16 · Well 14** · So 11 · Once 11 · If 9 · As 8 · When 7 · Instead 6.

Scripts using each word anywhere: And 93 · But 64 · If 49 · As 43 · When 36 · So 31 · **Actually 29** · Then 28 · Which 25 · Now 22 · You see 17 · Instead 16 · Once 16 · Because 16 · While 13 · After 13 · Until 9 · Eventually 7 · Finally 7.

| Family | Words | Job |
|---|---|---|
| Push | And, also, even | adds the next link; announces the last one (29 of 100 last sentences start with "And") |
| Turn | But, actually, instead, even though, in reality | breaks the expectation |
| Explain | You see, because, this is because, so, which, which means, meaning | answers the question the last sentence raised; "You see" is usually sentence 2 or 3 |
| Order | Then, once, as, when, after, next, until, eventually, finally | moves the clock one step |
| Set-up | If, now, well, imagine, what if | opens a scene or condition; "Now" resets the scene; "Well" answers a question just asked |
| Point back | This, these, he, she, it, the + thing | carries the last picture into the next sentence ("This creates…", "This makes…") |

Rules that follow:
1. Every sentence after the first opens with a glue word or a pointer back. A cold start sounds like a new topic.
2. "But" or "so", never "and then". His "And" always adds the next cause.
3. **The first "But" lands at a median 9.0 s (middle half 6.4-12.6 s)**, in 64 of 100. A sentence that starts with "But" is most often sentence 2 (23 times), then 3 or 4 (29).
4. "This" + verb carries the cause.
5. **Comma + "-ing" result** at the end of a sentence ("…, causing…", "…, making…", "…, saving…"): about half the scripts (53 of 100, 77 uses).
6. "Actually" is the small turn inside a sentence (29 scripts).

## 4. The seven story types
| Type | Shorts | Uses "But" | Typical length | Skeleton |
|---|---|---|---|---|
| How-it-works chain | 28 | 6 of 28 | 29 s | When/If you [moment] → As/Once [step] → Then [step] → This [causes] → And [result] |
| Myth flip | 24 | 23 of 24 | 30 s | If you [moment], you might think [belief] → But [truth] → You see [why] → Once [how] → And [payoff] |
| True story | 16 | 14 of 16 | 30 s | He/She/The [thing] mid-action → [step] → But [problem] → So [response] → And [outcome] → [sting] |
| Secret reason | 13 | 9 of 13 | 26 s | [strange fact] or "Have you ever noticed…" → Well / You see [reason] → [proof] → [punchline] |
| Do-this guide | 10 | 3 of 10 | 28 s | If you're [in trouble] → [the usual wrong move] → Instead [first move] → Once/Next [move] → [safe] |
| What-if ladder | 5 | 5 of 5 | 35 s | If you [small] → But if [bigger] → And if [biggest] → [scale or question] |
| Fable | 4 | 4 of 4 | ~60 s | a short tale mid-action with a moral twist |

**"But" lives in flips, stories and ladders. Chains and guides run on order words** (As, Once, Then, Next, This). Do not force a "But" into a chain; make each step cause the next. Name the story type before writing or scoring.

## 5. The last line
| Ending | Shorts | What it does |
|---|---|---|
| Result lands | 45 | the last step completes; you see the end state |
| Human sting | 25 | a person's fate, feeling or irony; the most surprising fact saved for last |
| Scale surprise | 9 | a size or number pinned to something familiar |
| Back to you | 8 | ties it to the viewer's world (why you take your shoes off at the airport) |
| Punchline | 8 | a blunt restatement of the reveal |
| Question | 4 | paradoxes only |
| Watch again | 1 | magic only |

The exact loop back to the opening picture is rare in the 100 (his biggest Short does it). Our series still ends on the first picture because the owner chose that; it is our rule, not his habit.

## 6. Example timelines (sentence start in seconds · first word · job)
- Myth flip, Saws That Stop For Fingers (120M): 0 If you (hook+belief) · 6.5 But (turn) · 9.1 You see (explain) · 15.3 Once (step) · 23.1 This (payoff).
- Chain, How Stitches Work (255M): 0 When you · 7.0 As · 14.5 Afterwards · 19.1 Then · 24.6 And (no "But").
- True story, The Prison Key Cake Escape (74M): 0 He · 6.1 The mold · 11.5 They · 14.5 But · 17.5 So · 21.6 And · 23.8 He (sting).
- Secret reason, Why One Shooter Gets A Blank Round (139M): 0 When a · 5.5 You see · 12.0 The soldiers · 19.0 This way (human sting).
- Guide, How To Remove Cactus Spines (96M): 0 If you · 5.0 And if (wrong move) · 11.1 So instead · 15.4 Once · 19.1 This.
- Ladder, How Strong Is Your Hair? (97M): 0 If you · 6.5 But if · 14.4 And if (scale).
