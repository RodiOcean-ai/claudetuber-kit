import React from 'react';
import { Composition } from 'remotion';
import { STYLES } from './styles';
import { DURATION, FPS, H, W } from './shared/timing';

export const Root: React.FC = () => (
  <>
    {STYLES.map((s) => (
      <Composition key={s.id} id={s.id} component={s.comp} durationInFrames={DURATION} fps={FPS} width={W} height={H} />
    ))}
  </>
);
