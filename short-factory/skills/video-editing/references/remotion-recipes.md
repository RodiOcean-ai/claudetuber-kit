# Remotion recipes for the video-editing moves (60 fps)

All components use `useCurrentFrame()` from the start of their `<Sequence>`. Import from `remotion`: `AbsoluteFill, Sequence, Img, OffthreadVideo, Audio, interpolate, Easing, useCurrentFrame, staticFile`.

## Text pop (70 % → 110 % in 7 frames → 100 % in 5)
```tsx
export const Pop: React.FC<{text: string; color?: string; glow?: string; size?: number}> = ({text, color = '#fff', glow = '#ffd21f', size = 110}) => {
  const f = useCurrentFrame();
  const ease = Easing.out(Easing.cubic);
  const s = f < 7 ? interpolate(f, [0, 7], [0.7, 1.1], {easing: ease}) : interpolate(f, [7, 12], [1.1, 1], {easing: ease, extrapolateRight: 'clamp'});
  const o = interpolate(f, [0, 3], [0, 1], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
    <div style={{transform: `scale(${s})`, opacity: o, fontFamily: 'Montserrat', fontWeight: 900, fontSize: size, color,
      WebkitTextStroke: '6px #111', paintOrder: 'stroke fill', textShadow: `0 0 24px ${glow}, 0 0 48px ${glow}`}}>{text}</div>
  </AbsoluteFill>;
};
```

## Typewriter
```tsx
const chars = Math.floor(interpolate(f, [0, text.length * 2], [0, text.length], {extrapolateRight: 'clamp'})); // 2 frames per letter
<span>{text.slice(0, chars)}</span>
```

## Line that draws itself ("trim paths") + glow
```tsx
const len = 600; const p = interpolate(f, [0, 30], [len, 0], {easing: Easing.inOut(Easing.cubic), extrapolateRight: 'clamp'});
<svg width={1920} height={1080} style={{filter: 'drop-shadow(0 0 8px #ffd21f)'}}>
  <path d="M300 540 C 700 300, 1200 800, 1600 540" stroke="#ffd21f" strokeWidth={8} fill="none" strokeDasharray={len} strokeDashoffset={p}/>
</svg>
```
(Measure the real path length with `getTotalLength()` once, or use `@remotion/paths` `evolvePath`.)

## Eased zoom with a fixed focus point
```tsx
// focus = the point that must stay put across cuts, in 0-1 of the frame (e.g. a rule-of-thirds point)
const z = interpolate(f, [0, dur], [1, 1.25], {easing: Easing.inOut(Easing.cubic)});
<AbsoluteFill style={{transform: `scale(${z})`, transformOrigin: `${focus.x * 100}% ${focus.y * 100}%`}}>{children}</AbsoluteFill>
```

## Blur-reveal box (flowchart beat)
```tsx
const b = interpolate(f, [revealAt, revealAt + 12], [14, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
<div style={{filter: `blur(${b}px)`}}>{heading}</div>
```

## Screen-blend overlay (light leak, electricity, dust)
```tsx
<AbsoluteFill style={{mixBlendMode: 'screen', opacity: 0.9}}><OffthreadVideo src={staticFile('overlays/leak_03.mp4')} muted/></AbsoluteFill>
```
For a transition: start the leak 8-10 frames before the cut and end it 10-15 after, peak brightness on the cut frame.

## Swipe / whip (also used by shorts-format)
Over 3-5 frames: outgoing layer `translateX(0 → -25%)` + `filter: blur(0 → 12px)`, incoming `translateX(25% → 0)` + `blur(12px → 0)`; whoosh on the middle frame.

## Parallax still (two layers)
Background 1.00 → 1.03, foreground cut-out 1.00 → 1.08 over the beat, both eased; foreground cut with a background-removal model (birefnet in ElevenCreative, priced, or a local tool).

## 3D tilt
`transform: perspective(1200px) rotateY(${interpolate(f,[0,20],[18,0],{easing: Easing.out(Easing.cubic)})}deg)`

## Mosaic / pixelate a region
Render the region from a downscaled copy (`width/24`) scaled back up with `imageRendering: 'pixelated'`.

## Glitch hit (2-4 frames)
Three copies of the layer, red/blue offset ±6 px with `mixBlendMode: 'screen'`, plus a random horizontal slice offset; only on a beat or a text pop.

## Mascot cut-out
A transparent PNG of our character, placed with eased position keyframes; one small "breathing" scale 1.00 ↔ 1.01 over 2 s so it never freezes.

## Text on black
`<AbsoluteFill style={{background: '#000'}}>` + the Pop or Typewriter; hold 1.2-2.5 s, with a riser into it or an impact on it.

## Sound placement
One `<Audio>` per effect inside a `<Sequence from={frame}>`; volume as a number (0-1) or a function of frame for fades. Whoosh 4-6 frames before the visual move peaks; impact exactly on the hit frame.
