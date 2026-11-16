---
name: channel-playbook
description: A general channel playbook for a faceless AI-voiced YouTube channel, from our measured study of one such channel (231k subs; all 9 long videos 154k-1.06M views) - picking a niche and outlier ideas, the story-driven "challenge/tutorial" long video (cold open + deal, hero's journey, try-diagnose-fix loop, mentor voice, deeper problem, twist ending), the studied shorts recipe (niche scroll, second-person problem script, step-by-step unfold, reveal ending, one consistent AI art style, post daily, judge at 24 h), the "viral recipe list", packaging, sponsors and the growth rules - and an end-to-end recipe for one story-driven faceless video using the story-scripts, natural-ai-voice, video-editing and thumbnail-design skills. Use when the owner asks for channel strategy, a niche, video ideas, a story-driven faceless video, a challenge video, a series format, "how do we grow the channel", posting plans, or when starting a new channel or series.
---

# Channel playbook: what to make, and how a whole video or channel fits together

Built from the 9 videos of the faceless-channel study (29 Oct 2026; your own downloads go in `<studies_root>/faceless-channel`, the shipped notes are in `${CLAUDE_PLUGIN_ROOT}/reference/creators/faceless-channel/`; full notes in `references/playbook-notes.md`). The four craft skills hold the details: **story-scripts**, **natural-ai-voice**, **video-editing**, **thumbnail-design**. This skill decides *what* to make and *how a whole video or channel* fits together.

**Copy the craft, never the identity:** no name of the studied creator, no ginger suit-and-tie mascot, no "Steven" friend, no his narrator voice, no his parody bits (Breaking Bad dream, Kung Fu Panda scroll), no his catchphrases. Our channel builds its own mascot, mentor and running jokes.
**Claude builds, the owner clicks.** Every spend is priced first; the owner presses Generate and Publish.

## The one rule
"Make people watch, and keep them watching." Trends and algorithms change; this doesn't. Win **retention first**, then clicks. And **value over retention**: never cut a useful part to please a chart.

## A. Channel decisions (free)
0. **A transformation, not a topic (I09):** "a niche is just a topic, and topics don't make people subscribe." Write what the ideal viewer walks away knowing or feeling ("people who make robotic videos learn to make them feel human"). That sentence is the channel.
1. **Niche:** scroll Shorts/TikTok/Reels (or the YouTube home page) for 2-3 hours and note what keeps showing up with high views from small channels. Good niches make the viewer **feel smart** ("business stories", "did-you-know" facts, "what if"). Shorts viewers want a quick lift, not doom. Step by step for a beginner: **yt-niche**.
2. **Outlier ideas:** in the niche, find videos that got far more views than their channel's average (5×+); those topics and formats are proven demand. Fast-growing new channels are the best source of current formats. Run `short-factory\scripts\topic_check.py` style overlap checks so we never remake a video.
3. **Brand from day one:** a person-style channel name (feels human, not a media company), one font, the 5-colour palette (thumbnail-design), one art style, a recurring mascot of our own. Open YouTube, TikTok and Instagram together. Written down once in the brand sheet: **yt-branding**.
4. **Invent a format and make a series of it (his biggest growth lever, I09):** one repeatable frame ("How I Actually [X]" is his: thumbnails, editing, voice, scripts). A viewer who likes one episode binges the rest, "average views per viewer" rises above 1, and every new episode lifts the old ones. A back catalogue in one format beats one viral video. Don't hunt a viral idea per video; find a format the audience likes. (YouTube Studio → Advanced mode → Average views per viewer.)
4b. **The Trojan horse:** nobody wants pure knowledge, so it rides inside a story, editing, animation and a script that entertain. Same information, different wrapping, different result.
5. **Skill > volume:** with a good team and tools, plan one strong video rather than posting 50 weak ones (his first video got 10k+ views and 1k subs); beginners with no skills should publish fast and improve one thing per batch of ~5.

## B. Story-driven long video (8-20 min) — the recipe
| Part | What happens | Skill |
|---|---|---|
| Cold open (0:00-1:00) | proof or a strong opinion in the first breath; a short skit with the mentor voice that ends in a **deal with a number and a deadline** ("1M views on one short in 7 days") or a mission | story-scripts |
| Title line | lands right after the skit, on an intro music sting | story-scripts |
| Sponsor (if any, 2-3 min in) | a scene inside the story world, or the sponsor's tool used for real in the project; snap back with a joke | story-scripts |
| Trials | day counter or numbered steps; each one a **try → result → diagnose (problem 1, 2, 3) → fix → try again** loop; a new beat every 30-60 s; a skit or mentor interruption every 2-4 min | story-scripts / editing |
| Midpoint | the mentor suggests the missing tool or idea | story-scripts |
| Crisis | the lowest point; the **deeper problem** is named here (patience, finishing, caring vs chasing numbers) | story-scripts |
| Reward + result | the lesson, then the act (publish, the result shown with real numbers) | |
| Twist ending (last 30-60 s) | an undercut: the success has a cost, the result is withheld, the challenger expected failure, or the topic flips (voice → dubbing). Abrupt, open, **no outro, no "subscribe"** | story-scripts |
| Voice | one designed narrator + one mentor voice, comped takes | natural-ai-voice |
| Edit | 1920×1080, 60 fps, a new view every ~4 s, music under ~90 % of it, whoosh/riser/impact sound design, text pops, overlays, eased zooms | video-editing |
| Thumbnail | mascot on the right third, 1-3 glowing words or a big number, one story prop | thumbnail-design |
| Description | 2 short paragraphs (the promise + "If you want to learn X, I'm sure you'll get something from this one"), chapters, a free guide link (lead magnet), tools list | `references/packaging.md` |

Stages and gates: brief → idea and title (gate) → plan and outline (gate) → script (gate) → voice batches (price, owner generates, comp, gate) → pictures and animation (price, gate per section) → edit (gate) → thumbnail A/B (price, gate) → package → owner publishes.

## C. Shorts recipe (his 7-day challenge, I04)
1. **Topic formula:** a cool topic + a surprising reveal + a sneaky tactic ("how a company made a tea-drinking country drink coffee"). No doom.
2. **Script (he went from flop to 21k views in 24 h, 96 % retention):** second person, the viewer IS the protagonist and the problem is in line one ("You run a giant company and you have a problem..."); unfold the solution step by step; the last line reveals the real company/person behind it; optionally close with a question to the viewer. Stakes in the hook, a real payoff at the end. (This is the same spine as **shorts-format**; use that skill to make it.)
3. **Visuals were the gap** once the script matched the best: one consistent AI art style; **storyboard by hand** (an AI shot list failed); image first, then animate each with very simple motion prompts; one multi-angle character sheet as the reference in every prompt.
4. **Voice:** natural-ai-voice in format mode, every silence cut.
5. **Edit:** short captions, music, sound effects, a few polish effects.
6. **Post** about one a day on YouTube, TikTok and Instagram. **Judge at 24 h** on two numbers only: "viewed vs swiped away" (his winners: 80 %+) and retention (his winners: ~90 %+). Don't wait for a flop to "warm up".
7. **Viral recipe list:** after ~10 shorts, re-watch your top ones and write down what they share (his: shorter subtitles, faster scene changes, a sound effect in the first second, a joke at the end). Re-do it when views drop: recipes decay.

## C2. Mindset rules the studied creator teaches (I09, I05)
- **Learn out loud:** be the friend a few steps ahead, not the guru; what feels obvious to us is new to someone. Honest guides beat expert lectures.
- **Don't compare chapter 1 with someone's chapter 100.** He made 100+ unwatched videos on an earlier channel before "blowing up with 8".
- **Fix one thing per video:** the weakest part of the last one; ignore the rest until it's good.
- **To learn, recreate** a video you admire for practice (never publish the copy).
- **Outliers:** a video at 10-100× its channel's normal views; watch it to the end and write down why it worked (thumbnail? intro? story?).

## D. Rules the studied creator holds against common advice
- One planned strong video beats 25-50 rushed ones (if you have the skills).
- "Beginning, middle, end" is useless advice; use the 12-beat hero's journey.
- Mass-produced AI videos get no views; AI belongs inside a crafted video.
- AI can't plan your shots or write your script; it can roast them.
- Copying the niche's look makes you invisible; borrow from other niches.
- Reused content without real transformation (voice, story, editing) gets demonetised. Every video needs our own narration and story.

## E. After posting
- Pin a comment with a question (not "subscribe").
- Dub into Spanish, Hindi and Portuguese with the natural-ai-voice dubbing stage.
- Log views at 24 h, 7 days and 28 days, click-through rate, average view duration and "views by audio track" in `JOURNEY.md`.
- Pick one new technique to learn for the next video (video-editing).

## Reference files
- `references/playbook-notes.md`: per-video breakdowns (hooks, arcs, deeper problems, twists, sponsors, methods), the full shorts recipe, cross-video patterns.
- `references/packaging.md`: his title formats, description template and tags.
- `references/study-data.md`: the measured numbers for all 9 videos.

Source: our own analysis of public videos from Isaac (@isaacverse). Not affiliated with or endorsed by Isaac or @isaacverse.
