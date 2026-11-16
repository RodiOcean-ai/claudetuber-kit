# How AI-text detectors (GPTZero and others) judge a script: notes from YouTube, 7 Nov 2026

Why this file exists: the owner tested our drplants-long scripts on GPTZero (v15 and v17: 100 % AI; Paddy Galloway's own transcript: 100 % human) and asked how GPTZero decides, "instead of guessing". Summaries in our words, not quotes.

## Sources watched (transcripts read)
1. Dr Kriukow, "How does AI detection work? I designed an EXPERIMENT to show you" (38K views, 1 y, AEoQqVVAn-s)
2. CBC News, "Creator of ChatGPT detector answers your questions about generative AI" (Edward Tian, GPTZero founder; 12K, 2023, JGYQg2snF34)
3. The Nerdy Novelist, "GPTZero Review 2026: Is This AI Detector Actually the BEST?" (23K, 7 mo, hPyHIHW4lcI)
4. Dr Theresa Orr, "AI-Detectors Just Changed Everything...Again" (46K, 1 y, L51rkfbJ858)

## What they show
- **The whole document is judged together, not sentence by sentence** (1). His test: an AI chapter split in two, each half hand-rewritten until a free checker showed 0 % AI; pasted back together and scanned as one document: 100 % AI. Human sentences sitting between AI sections also get flagged, just by being near them.
- **It compares the text with huge sets of known human and known AI documents**, looking at how likely that combination of expressions is to appear together (1). The founder's plain version: AI repeats the most common patterns it has seen (2).
- **Editing every sentence does not clear it** (3): an AI chapter that humans edited so that almost every sentence changed still scored 87 % AI (pure AI fiction: 66 %; pure AI non-fiction: 95 %).
- **Factual, explaining writing is flagged more, even when human** (3): his own pre-AI non-fiction article scored 53 % AI; human fiction 0 %. Our scripts are explainers, the riskiest kind.
- **Polish itself is a signal** (4): perfect grammar, repeated structure, smooth fluent writing. Grammar tools and "humanizer"/paraphrase tools now get flagged too; the newer detectors look for humanizer patterns as well.
- **What protects real people** (4): writing in your own voice, not over-polishing, keeping a record of the process.

## What it means for us (checked against our own tests)
- Rewriting an AI draft line by line, or swapping in less likely words, will not move GPTZero: it reads the whole script's patterns and polish. This matches what happened: v16 and v17 kept every structure and still scored 100 % AI.
- Two free local detectors we built (Binoculars on Qwen2.5-0.5B; desklib DeBERTa classifier) both failed calibration on our material: see tools/humanizer/NOTES.md.
- What scored human was text that started as a person talking (Paddy's transcript).
- **Working method:** Claude does the research, facts, structure, beats, hooks and numbers as NOTES (not sentences); the owner talks each part in his own words (Transcript Recorder, notes mode); Claude turns the take into text and only cuts, reorders and fixes facts, with a light hand, never polishing it smooth. One GPTZero scan at the end.
