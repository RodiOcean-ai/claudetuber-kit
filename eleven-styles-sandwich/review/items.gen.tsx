// Written by review/make_items.py from review/contract.json on 2026-11-16.
// Do not edit by hand: change the contract and run  python review/make_items.py  again.
import React from 'react';
import { Kinetic as C0 } from '../src/styles/s01_kinetic/Kinetic';
import { MotionGraphics as C1 } from '../src/styles/s02_motion/MotionGraphics';
import { Screencast as C2 } from '../src/styles/s03_screencast/Screencast';
import { Isometric as C3 } from '../src/styles/s04_isometric/Isometric';
import { Whiteboard as C4 } from '../src/styles/s05_whiteboard/Whiteboard';
import { Comic as C5 } from '../src/styles/s06_comic/Comic';
import { TwoPointFiveD as C6 } from '../src/styles/s07_25d/TwoPointFiveD';
import { Collage as C7 } from '../src/styles/s08_collage/Collage';
import { CharacterStory as C8 } from '../src/styles/s09_character/CharacterStory';
import { ThreeD as C9 } from '../src/styles/s10_3d/ThreeD';
import { StopMotion as C10 } from '../src/styles/s11_stopmotion/StopMotion';
import { Whiteboard3D as C11 } from '../src/styles/t05_whiteboard3d/Whiteboard3D';
import { Comic3D as C12 } from '../src/styles/t06_comic3d/Comic3D';

export const TITLE = "Eleven styles, one sandwich";
export const FPS = 30;
export type ReviewItem = {
  id: string; n: string; name: string; frames: number; w: number; h: number; start: number;
  chapter: string | null; timeline: boolean; music: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  comp: React.ComponentType<any>;
};
export const ITEMS: ReviewItem[] = [
  { id: "S01-KineticTypography", n: "1", name: "Kinetic typography", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C0 },
  { id: "S02-MotionGraphics", n: "2", name: "Motion graphics", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C1 },
  { id: "S03-Screencast", n: "3", name: "Screencast", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C2 },
  { id: "S04-Isometric", n: "4", name: "Isometric", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C3 },
  { id: "S05-Whiteboard", n: "5", name: "Whiteboard", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C4 },
  { id: "S06-Comic", n: "6", name: "Comic", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C5 },
  { id: "S07-TwoPointFiveD", n: "7", name: "2.5D", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C6 },
  { id: "S08-Collage", n: "8", name: "Collage", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C7 },
  { id: "S09-CharacterStory", n: "9", name: "2D characters with a story", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C8 },
  { id: "S10-ThreeD", n: "10", name: "3D animation", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C9 },
  { id: "S11-StopMotion", n: "11", name: "Stop motion", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C10 },
  { id: "T05-WhiteboardThreeJS", n: "5", name: "Whiteboard, three.js test", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C11 },
  { id: "T06-ComicThreeJS", n: "6", name: "Comic, three.js test", frames: 450, w: 1920, h: 1080, start: 0, chapter: null, timeline: true, music: true, comp: C12 },
];
