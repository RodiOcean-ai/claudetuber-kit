import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile } from 'remotion';
import { FPS } from './kit';
import { Captions, Word } from './captions';
import words from './words.json';          // captions.py: Whisper timing, the script's spelling
import starts from './captions.json';      // captions.py: word numbers where each 1-3 word caption starts
import music from './music.json';          // music_pick.py: {track, file, music_in, hit_at}
import swishes from './swishes.json';      // blender_tools.py whips: seconds of the big camera whips (2-5 of them)
import { BrandLayer } from './brand';      // RodiOcean brand: ping, proof readout, sea wave (switched in brand.json)

/* short-factory edit: ONE continuous Blender flight (clips/world.mp4, no cuts), the voice from frame one, 1-3 word captions,
   the rotating music bed placed so its final hit lands on the last word (frame one on a beat, so the loop keeps the groove),
   and a soft swish on each big camera whip. Loudness is mastered afterwards by render.sh (-12 LUFS, -1 dBTP). */
const W = words as Word[];
export const END = W[W.length - 1].e + 0.5;
export const FRAMES = Math.round(END * FPS);
const MUSIC = 0.18;                        // about 16 LU under the voice (format benchmark: 14-18)

export const Short: React.FC = () => (
  <AbsoluteFill style={{ background: '#dcecff' }}>
    <OffthreadVideo src={staticFile('clips/world.mp4')} muted />
    <BrandLayer />
    <Captions words={W} starts={starts as number[]} />
    <Audio src={staticFile('audio/voice.wav')} />
    <Audio src={staticFile(music.file)} trimBefore={Math.round(music.music_in * FPS)} volume={MUSIC} />
    {(swishes as number[]).map((t, i) => (
      <Sequence key={i} from={Math.round(t * FPS)} durationInFrames={15}>
        <Audio src={staticFile(`audio/swish${(i % 3) + 1}.wav`)} volume={0.35} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
