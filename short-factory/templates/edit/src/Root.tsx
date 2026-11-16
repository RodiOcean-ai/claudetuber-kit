import React from 'react';
import { Composition } from 'remotion';
import { Short, FRAMES } from './Short';

export const RemotionRoot: React.FC = () => (
  <Composition id="Short" component={Short} durationInFrames={FRAMES} fps={30} width={1080} height={1920} />
);
