import { Config } from '@remotion/cli/config';
// three.js styles need the graphics card in the headless browser
Config.setChromiumOpenGlRenderer('angle');
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
