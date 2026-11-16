# Thumbnail prompts (gpt-image-2.5-sunburst, 16:9, 2K, medium)

## Base block (always)
> YouTube thumbnail, 16:9. Rule-of-thirds layout: [MAIN SUBJECT] on the right third line, [PROP] in the left-centre, clean space along the top third for a headline. Bold, high-contrast digital illustration with crisp edges, strong rim light and a soft outer glow around every main shape. Palette: deep [black/navy] background, white highlights, [MAIN COLOUR] as the hero colour, [HIGHLIGHT COLOUR] as the accent for this video. One focal point, readable at small size, no clutter, no small details.

## Text block (when the model renders the text)
> Headline across the top in huge bold [MAIN COLOUR] capitals with a thick dark outline and a bright outer glow: "[1-3 WORDS]". Spelled exactly like that, no other text anywhere.
Otherwise end with: "No text, no letters, no logos." and add text in `thumb_finish.py`.

## Type add-ons
- **Shock:** "[SUBJECT] reacting with wide eyes as [SHOCKING MOMENT] happens beside him, frozen at the peak moment."
- **Big number:** "a glowing [phone screen / counter / chart] showing "[NUMBER]" with a green up arrow, the number large and crisp."
- **Hidden:** add the item normally; pixelate it in `thumb_finish.py --pixelate x,y,w,h`. Image models blur unreliably.
- **Simple:** "a single [OBJECT] on a plain [COLOUR] background, studio light, nothing else in frame."
- **Comparison:** "split vertically: left [CHEAP/BEFORE] in dull colours, right [EXPENSIVE/AFTER] in vivid colours, a thin glowing divider."
- **Creator + bigger thing:** "[MASCOT from the reference] small in the lower right, looking up at a gigantic [THING] that fills the left two thirds."

## Mascot block (our own mascot only)
> The character from the reference sheet, same face, hair, outfit and colours, [EXPRESSION: serious / smug / alarmed], looking slightly off-camera toward the prop.
