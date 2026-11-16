import React from 'react';
import { AbsoluteFill } from 'remotion';
import { Soundtrack } from '../shared/Soundtrack';
import { ensureFonts } from '../shared/fonts';

ensureFonts('Inter');
export const Placeholder: React.FC<{ n: number; name: string }> = ({ n, name }) => (
  <AbsoluteFill style={{ background: '#ECF7FD', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter', color: '#0B2540' }}>
    <div style={{ fontSize: 44, fontWeight: 600, opacity: 0.6 }}>Style {n}</div>
    <div style={{ fontSize: 110, fontWeight: 800 }}>{name}</div>
    <div style={{ fontSize: 40, fontWeight: 500, opacity: 0.6, marginTop: 20 }}>not built yet</div>
    <Soundtrack />
  </AbsoluteFill>
);
