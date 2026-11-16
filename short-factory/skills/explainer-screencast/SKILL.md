---
name: explainer-screencast
description: Make an explainer clip in SCREENCAST style with Remotion - a believable screen recording of a made-up app (window, toolbar, sidebar, canvas, steps panel) where a real-looking cursor drags, clicks, paints and draws with click ripples and real click sounds, the camera auto-zooms on whatever the cursor is doing (the Screen Studio look), a checklist ticks itself off and the ending is a toast with a button and confetti. Approved first time (14 Nov 2026, 0 notes). Use whenever the owner says "screencast", "screen recording style", "fake app", "show it in an app", "cursor animation", "auto zoom", "tutorial screen", or with explainer-styles for a multi-style test.
---

# Screencast: a made-up app, a real-feeling cursor

Read `explainer-styles` first. Rank 3 of 11; 4 minutes to a first build, approved with no notes.

## The reusable pattern (`reference/Screencast.tsx`)
1. **Lay the app out in screen pixels** (window 1620 x 940, title bar with traffic lights, toolbar of tools, sidebar list,
   canvas with dotted grid, a right panel with steps and a live number). Everything the cursor touches has a known
   coordinate (list rows, tool buttons, drop spots) so paths and clicks line up.
2. **The cursor path** is a list of [frame, x, y] keys: eased moves with a slight arc (like a hand on a mouse), straight
   lines while painting; hold keys for clicks. Clicks = small press-scale + an expanding ring + a click sound.
3. **Drag = the item follows the cursor** between the press and the drop key; it lands on the board with a small spring.
4. **Painting reveals** the result through an SVG mask of circles placed at every cursor position since the paint started;
   the coverage number counts the same progress.
5. **The camera** zooms between keys [frame, zoom, centre x, y] with an ease-in-out (1.0 -> 1.4-1.75 on the action, back to
   1.0 for the end): this is what makes it feel like a modern recorded tutorial.
6. The tool changes the cursor (arrow, knife, crosshair) and the toolbar highlight; a hold-to-press ring fills during the
   press.

## Pitfalls
- Sidebar rows under a search box: compute row positions from the real layout, or the cursor clicks between items.
- A drawn line must follow the cursor exactly (draw it to the cursor's current position, not a separate timer).
- Pop-ups (toasts) must sit inside the canvas, never over the steps panel the viewer is reading.

## Numbers (14 Nov 2026)
Build 4 min (1 self-check round), 0 owner notes, render 19.4 s, 6.0 MB.
