// Fonts from local files (copied from @fontsource into public/fonts), so the studio, the review page and the render agree.
import { loadFont } from '@remotion/fonts';
import { staticFile } from 'remotion';

type Face = [file: string, weight: string, style?: 'normal' | 'italic'];
const FACES: Record<string, Face[]> = {
  Inter: [400, 500, 600, 700, 800, 900].map((w) => [`inter-latin-${w}-normal.woff2`, `${w}`] as Face),
  'JetBrains Mono': [500, 700, 800].map((w) => [`jetbrains-mono-latin-${w}-normal.woff2`, `${w}`] as Face),
  'Instrument Serif': [['instrument-serif-latin-400-normal.woff2', '400'], ['instrument-serif-latin-400-italic.woff2', '400', 'italic']],
  'Space Grotesk': [500, 700].map((w) => [`space-grotesk-latin-${w}-normal.woff2`, `${w}`] as Face),
  Rubik: [500, 700, 800, 900].map((w) => [`rubik-latin-${w}-normal.woff2`, `${w}`] as Face),
  Anton: [['anton-latin-400-normal.woff2', '400']],
  Caveat: [500, 700].map((w) => [`caveat-latin-${w}-normal.woff2`, `${w}`] as Face),
  Bangers: [['bangers-latin-400-normal.woff2', '400']],
  'Comic Neue': [400, 700].map((w) => [`comic-neue-latin-${w}-normal.woff2`, `${w}`] as Face),
  Fredoka: [500, 600, 700].map((w) => [`fredoka-latin-${w}-normal.woff2`, `${w}`] as Face),
  'Abril Fatface': [['abril-fatface-latin-400-normal.woff2', '400']],
  'Bebas Neue': [['bebas-neue-latin-400-normal.woff2', '400']],
  'Courier Prime': [400, 700].map((w) => [`courier-prime-latin-${w}-normal.woff2`, `${w}`] as Face),
  'Patrick Hand': [['patrick-hand-latin-400-normal.woff2', '400']],
  'Permanent Marker': [['permanent-marker-latin-400-normal.woff2', '400']],
};
const done = new Set<string>();
export const ensureFonts = (...families: (keyof typeof FACES)[]) => {
  for (const fam of families) {
    if (done.has(fam)) continue;
    done.add(fam);
    for (const [file, weight, style] of FACES[fam]) {
      loadFont({ family: fam, url: staticFile(`fonts/${file}`), weight, style: style ?? 'normal' }).catch(() => undefined);
    }
  }
};
