// The same voice and music under every style; each style adds its own sound effects.
import React from 'react';
import { Audio, Sequence, staticFile } from 'remotion';

export type Sfx = { at: number; file: string; vol?: number; dur?: number };
export const Soundtrack: React.FC<{ sfx?: Sfx[] }> = ({ sfx = [] }) => (
  <>
    <Audio src={staticFile('audio/voice.wav')} />
    <Audio src={staticFile('audio/music.wav')} />
    {sfx.map((s, i) => (
      <Sequence key={i} from={Math.max(0, Math.round(s.at))} durationInFrames={s.dur ?? 60} layout="none">
        <Audio src={staticFile(`sfx/${s.file}`)} volume={s.vol ?? 0.5} />
      </Sequence>
    ))}
  </>
);
