# Human writing: making a script not sound AI-written (version 1)

Two sources:
- **The faceless-channel study's 4th element of a human voice:** if AI writes the script, no voice setting can save it ("if you write your scripts with AI and think nobody knows, trust me, we know").
- **Our own test (Didit contest form, Oct 2026):** the description went from AI-flagged to **99 % human on GPTZero** with the changes below.
The owner wants a deeper study of this later; extend this file then.

**Update 7 Nov 2026 (GPTZero Model 5.0b):** the original Didit text still scores 86 % human. What passes is plain statements of what happens with almost no commentary, written like a quick message. Style tweaks that keep commenting lines (fragments, asides, opinions, typos, lower case) still score 100 % AI.

## What gives AI text away
1. **Predictable words.** Each next word is the most likely one. People pick odder ones.
2. **Even rhythm.** Sentences of similar length and shape. People write in bursts.
3. **Tidy patterns.** Groups of three, smooth "So... Then... Finally" links, stock phrases ("a song you can't get out of your head", "in today's fast-paced world", "let's dive in", "game-changer", "unlock").

## The fixes (each one measured on our form text)
- **Spread sentence lengths** from 1 word to 35-45. Target in `script_check.py`: length spread (standard deviation) of 6 words or more (the studied creator measures 6.5-7.3, average sentence about 10 words), at least one sentence of 3 words or fewer per 100 words.
- **Fragments and asides.** "Song first." "Nobody caught it until late." "Be honest."
- **Less polished, more specific choices.** "gave up arguing with it", "binned", "a doctor who has never smiled in his life". Specific beats general every time.
- **Break the triples.** Two items, or four, or one with a twist.
- **Throw lines away.** The line a detector flags most (usually a slogan) goes in brackets or becomes a throwaway aside.
- **Talk to someone.** Questions to the viewer, small admissions ("At least, that's what usually happens for me").
- **Self-correction and hesitation, written in:** "So, in this video we're... no, wait." These also make the AI voice perform better (natural-ai-voice).
- **Opinions.** He disagrees with common advice ("I completely disagree with that, and I have evidence"). An opinion is the most human thing in a script.

## What not to do
- Don't fake typos or bad grammar in narration; the voice reads them oddly.
- Don't stuff fillers into every line. 1-3 per minute of narration is plenty (see natural-ai-voice for his measured rate).
- Don't run the text through an online "humanizer" or rewriter (paid tools; they also make it generic again).
