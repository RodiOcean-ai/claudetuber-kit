# Topics and titles on the shorts format

## What a format topic is
One concrete question a curious 12-year-old would ask, whose answer is **a picture you have never seen**. Test every idea with these 5 questions; it needs at least 4 yeses:
1. **Can you see it?** Inside the body, an object at an absurd scale, a physical event in slow motion, a world-wide "what if". No abstract ideas, no money talk.
2. **Is there a familiar object** to anchor it? (stitches, a splinter, a McFlurry spoon, toenails, a bullet, a firing squad, candy)
3. **Is the answer surprising** and still true? Is there a wrong belief to flip with "But…"?
4. **Does the answer fit in 30 s** and about 85 words?
5. **Body, danger or scale?** A tiny wince ("ouch", "gross", "no way") is his strongest engine: 😨 🤮 😱.

## Angle families (with his results)
| Family | Pattern | His examples (views) |
|---|---|---|
| Body mechanism | How/Why does [body thing] happen? | How Stitches Work (255M), How Splinters Get Unstuck (216M), Blown Veins (139M), Why Bees Die After They Sting You (115M) |
| Everyday object secret | The reason [object] looks/works like this | The Reason The McFlurry Spoon Looks Weird (166M), How Gas Pumps Know When To Stop (87M) |
| Scale "if you…" | If you [did impossible thing with the body / everyone], how big/long? | How Long Are Your Blood Vessels? (157M), An Island Of Toenail Clippings? (140M) |
| Could X survive Y | Could/Can [object] stop/survive [force]? | Could Ancient Armor Stop Bullets? (156M), Can A WW2 Helmet Stop A Bullet? (52M), Can A Fly Dodge A Bullet? (55M) |
| What if (world) | What if [everyone/the Earth/you] [did X]? | What If The Earth Stopped Rotating? (46M), What If The World Only Had Two People? (41M) |
| Odd true war/history fact | [Odd thing] used in war? / Why [historic practice]? | Tootsie Rolls Used In War? (124M), Why One Shooter Gets A Blank Round (139M), Why Did People Put Bells On Graves? (108M) |
| Survival what-to-do | What to do if [danger] | What To Do If You Puncture A Lung (87M), How To Escape A Car Trunk (105M) |

## What flops on his channel (1-2M views, avoid)
Celebrity and business gossip, lawsuits, rich people's secrets, "the government doesn't want you to see this", how-to crafts (paper folding, card tricks), sports technique, and anything that needs a long backstory before the picture.

## Generating 5 angles from the owner's topic
1. Write 10 raw questions about the topic, at least 2 from each of: body, scale, could-it-survive, what-if, odd fact.
2. Score each on the 5 tests; keep the top 5. At least 2 should be "what if / could you" angles (the owner wants what-ifs).
3. Run the topic check on all 5:

       <python> -I -X utf8 "${CLAUDE_PLUGIN_ROOT}\scripts\topic_check.py" --channel shorts-format "<title 1>" "<title 2>" …

   - TOO CLOSE: drop it.
   - LOOK CLOSELY: read his title; change the angle if it's the same question.
   - If a very similar title of his did well, that proves the theme, but our angle must be new.
4. Present each as: the title, one line on the picture it gives, the wince or wow, and an honest risk (hard to animate, facts uncertain).

## Title formula
`[How / Why / What If / Could / Can / The Reason] + [familiar object or "you"] + [the twist] + ?` + ONE emoji at the end.
- 4-8 words. Plain words. Title case. A question mark when it is a question.
- Emoji by emotion: 🤔 curious (his most used), 😮 surprising, 😨 / 😱 scary, 🤮 / 🤢 gross, 😳 awkward, 🤯 mind-blowing, 🤨 suspicious-odd.
- Optional tail he uses: "(explained)", "(How?)", "(ouch)". Use them rarely.
- Never clickbait the picture away: the title asks, the first line repeats it, the first frame shows it.
