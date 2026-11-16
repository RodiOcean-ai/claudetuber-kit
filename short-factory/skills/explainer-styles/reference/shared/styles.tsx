// The 11 styles (easiest first, the owner's ranking of 14 Nov 2026). `built` = ready for the owner's review page.
import React from 'react';
import { Placeholder } from './styles/Placeholder';
import { Kinetic } from './styles/s01_kinetic/Kinetic';
import { MotionGraphics } from './styles/s02_motion/MotionGraphics';
import { Screencast } from './styles/s03_screencast/Screencast';
import { Isometric } from './styles/s04_isometric/Isometric';
import { CharacterStory } from './styles/s09_character/CharacterStory';
import { Whiteboard } from './styles/s05_whiteboard/Whiteboard';
import { Comic } from './styles/s06_comic/Comic';
import { ThreeD } from './styles/s10_3d/ThreeD';
import { StopMotion } from './styles/s11_stopmotion/StopMotion';
import { Collage } from './styles/s08_collage/Collage';
import { TwoPointFiveD } from './styles/s07_25d/TwoPointFiveD';
import { Whiteboard3D } from './styles/t05_whiteboard3d/Whiteboard3D';
import { Comic3D } from './styles/t06_comic3d/Comic3D';

export type StyleDef = { id: string; n: number; name: string; comp: React.FC; built: boolean };
const todo = (n: number, name: string): React.FC => () => <Placeholder n={n} name={name} />;

export const STYLES: StyleDef[] = [
  { id: 'S01-KineticTypography', n: 1, name: 'Kinetic typography', comp: Kinetic, built: true },
  { id: 'S02-MotionGraphics', n: 2, name: 'Motion graphics', comp: MotionGraphics, built: true },
  { id: 'S03-Screencast', n: 3, name: 'Screencast', comp: Screencast, built: true },
  { id: 'S04-Isometric', n: 4, name: 'Isometric', comp: Isometric, built: true },
  { id: 'S05-Whiteboard', n: 5, name: 'Whiteboard', comp: Whiteboard, built: true },
  { id: 'S06-Comic', n: 6, name: 'Comic', comp: Comic, built: true },
  { id: 'S07-TwoPointFiveD', n: 7, name: '2.5D', comp: TwoPointFiveD, built: true },
  { id: 'S08-Collage', n: 8, name: 'Collage', comp: Collage, built: true },
  { id: 'S09-CharacterStory', n: 9, name: '2D characters with a story', comp: CharacterStory, built: true },
  { id: 'S10-ThreeD', n: 10, name: '3D animation', comp: ThreeD, built: true },
  { id: 'S11-StopMotion', n: 11, name: 'Stop motion', comp: StopMotion, built: true },
  // tests asked for on 14 Nov 2026: styles 5 and 6 made with three.js instead of the picture maker
  { id: 'T05-WhiteboardThreeJS', n: 5, name: 'Whiteboard, three.js test', comp: Whiteboard3D, built: true },
  { id: 'T06-ComicThreeJS', n: 6, name: 'Comic, three.js test', comp: Comic3D, built: true },
];
