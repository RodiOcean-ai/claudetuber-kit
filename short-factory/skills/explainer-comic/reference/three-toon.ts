// The cartoon look for three.js (comic and whiteboard tests without the picture maker, 14 Nov 2026):
// flat toon shading in 3 bands with comic halftone dots in the shadows, and black ink outlines (an "inverted hull":
// the same shape drawn inside-out, pushed outwards by a fixed number of pixels, so every outline has the same width).
import * as THREE from 'three';
import { mergeVertices } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

/** Outline width (px of the current viewport) and the viewport size; set both before every render call. */
export const INK_U = { thickness: { value: 3 }, resolution: { value: new THREE.Vector2(1000, 1000) } };
/** Halftone dots: cell size in device pixels, strength 0 (off) .. 1. */
export const HT_U = { cell: { value: 9 }, strength: { value: 0.42 } };

let ramp: THREE.DataTexture | null = null;
const toonRamp = () => {
  if (ramp) return ramp;
  ramp = new THREE.DataTexture(new Uint8Array([95, 175, 255]), 3, 1, THREE.RedFormat);
  ramp.minFilter = ramp.magFilter = THREE.NearestFilter;
  ramp.generateMipmaps = false;
  ramp.needsUpdate = true;
  return ramp;
};

/** A toon material: three flat light bands, plus round halftone dots where the light is low (screen-space grid at 45 deg). */
export const toonMat = (color: THREE.ColorRepresentation, extra: THREE.MeshToonMaterialParameters = {}) => {
  const m = new THREE.MeshToonMaterial({ color, gradientMap: toonRamp(), ...extra });
  m.onBeforeCompile = (sh) => {
    sh.uniforms.htCell = HT_U.cell;
    sh.uniforms.htStrength = HT_U.strength;
    sh.fragmentShader = 'uniform float htCell;\nuniform float htStrength;\n' + sh.fragmentShader.replace('#include <opaque_fragment>', `
      {
        vec3 lf = outgoingLight / max(diffuseColor.rgb, vec3(0.04));
        float light = dot(lf, vec3(0.3333));
        vec2 q = gl_FragCoord.xy / htCell;
        q = vec2(q.x + q.y, q.y - q.x) * 0.70710678;
        float r = clamp((0.9 - light) / 0.55, 0.0, 1.0) * 0.47;
        float dd = length(fract(q) - 0.5);
        float dotm = (1.0 - smoothstep(r - 0.07, r + 0.07, dd)) * step(0.03, r);
        outgoingLight *= 1.0 - htStrength * dotm;
      }
      #include <opaque_fragment>`);
  };
  m.customProgramCacheKey = () => 'toon-halftone-v1';
  return m;
};

/** The ink: the hull is drawn from the back side only and pushed out along its smoothed normals in screen space. */
export const inkMat = (color = '#121212') => new THREE.ShaderMaterial({
  uniforms: { thickness: INK_U.thickness, resolution: INK_U.resolution, inkColor: { value: new THREE.Color(color) } },
  vertexShader: `
    uniform float thickness;
    uniform vec2 resolution;
    void main() {
      vec4 clip = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      vec3 n = normalize(normalMatrix * normal);
      vec2 d = (projectionMatrix * vec4(n, 0.0)).xy;
      float l = length(d);
      d = l > 1e-5 ? d / l : vec2(0.0);
      clip.xy += d * (thickness * 2.0 / resolution) * clip.w;
      gl_Position = clip;
    }`,
  fragmentShader: `
    uniform vec3 inkColor;
    void main() { gl_FragColor = vec4(inkColor, 1.0); }`,
  side: THREE.BackSide,
});

const INK = inkMat();
const hullCache = new WeakMap<THREE.BufferGeometry, THREE.BufferGeometry>();
/** The same shape with welded corners and smooth normals (so the pushed-out hull has no gaps at sharp edges). */
export const hullGeo = (g: THREE.BufferGeometry) => {
  const hit = hullCache.get(g);
  if (hit) return hit;
  let h = g.clone();
  for (const k of Object.keys(h.attributes)) if (k !== 'position') h.deleteAttribute(k);
  h = mergeVertices(h, 1e-4);
  h.computeVertexNormals();
  h.clearGroups();
  hullCache.set(g, h);
  return h;
};

/** Give a mesh its ink outline (a child mesh, so it follows every move, turn and squash of the mesh). */
export const ink = <T extends THREE.Mesh>(mesh: T, on = true): T => {
  if (!on) return mesh;
  const hull = new THREE.Mesh(hullGeo(mesh.geometry), INK);
  hull.castShadow = false;
  hull.receiveShadow = false;
  hull.name = 'ink';
  mesh.add(hull);
  return mesh;
};

/** A capsule from a to b (radius r), e.g. a cartoon finger. */
export const capsule = (a: THREE.Vector3, b: THREE.Vector3, r: number, mat: THREE.Material) => {
  const d = new THREE.Vector3().subVectors(b, a);
  const len = Math.max(0.0001, d.length());
  const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 6, 20), mat);
  m.position.copy(a).addScaledVector(d, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize());
  return m;
};
