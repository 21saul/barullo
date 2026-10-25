import { useThree } from '@react-three/fiber';
import React, { useLayoutEffect, useMemo } from 'react';
import * as THREE from 'three';
import { C, osc, oscCos } from '../lib/tokens';

/**
 * Cabeza hyperpop en 3D real (three.js), renderizada en diferido por Remotion.
 * Lo que la acerca a las referencias es material y luz: clearcoat en la piel,
 * cromo metalness 1 reflejando un estudio de paneles chicle/violeta/blanco,
 * perlas con iridiscencia. La geometría es deliberadamente estilizada.
 *
 * Unidades: la cabeza mide ~2,3 de alto, centrada en el origen, mirando a +z.
 * `t` = fase 0..1 del bucle; todo es periódico.
 */

// --- Forma de la cabeza --------------------------------------------------
// Perfil de huevo: cráneo ancho, barbilla estrecha (cara de bebé de las refs).
const HEAD_H = 1.15;
const radiusAt = (yn: number) => {
  // yn en [-1, 1] (barbilla → coronilla)
  const theta = Math.acos(-yn);
  return Math.sin(theta) * (0.98 + 0.13 * yn - 0.06 * yn * yn);
};
const Z_SCALE = 0.9;

/** Punto de la superficie de la cara en (x, y), para pegar rasgos. */
const surf = (x: number, y: number, inset = 0): [number, number, number] => {
  const r = radiusAt(Math.max(-0.999, Math.min(0.999, y / HEAD_H)));
  const z = Math.sqrt(Math.max(0, r * r - x * x)) * Z_SCALE;
  return [x, y, z - inset];
};

const useHeadGeometry = () =>
  useMemo(() => {
    const pts: THREE.Vector2[] = [];
    const N = 64;
    for (let i = 0; i <= N; i++) {
      const yn = -1 + (2 * i) / N;
      pts.push(new THREE.Vector2(Math.max(0.0001, radiusAt(yn)), yn * HEAD_H));
    }
    // phiStart = π deja la costura detrás y el centro de la textura (u=0,5) delante.
    const g = new THREE.LatheGeometry(pts, 128, Math.PI);
    g.scale(1, 1, Z_SCALE);
    g.computeVertexNormals();
    return g;
  }, []);

// --- Maquillaje pintado en una textura de canvas (local, sin archivos) -----
const useSkinTexture = () =>
  useMemo(() => {
    const W = 2048;
    const H = 1024;
    const cv = document.createElement('canvas');
    cv.width = W;
    cv.height = H;
    const g = cv.getContext('2d')!;
    // Base: lila lechoso más rosado hacia abajo (subsurface).
    const base = g.createLinearGradient(0, 0, 0, H);
    base.addColorStop(0, '#EBD3F6');
    base.addColorStop(0.55, '#F6DDF2');
    base.addColorStop(1, '#E7B9EC');
    g.fillStyle = base;
    g.fillRect(0, 0, W, H);
    // u → x: el frente es u=0,5. v → y: arriba del canvas = coronilla.
    const blob = (u: number, v: number, rx: number, ry: number, color: string, a: number) => {
      const x = u * W;
      const y = (1 - v) * H;
      const grd = g.createRadialGradient(x, y, 0, x, y, 1);
      const c = new THREE.Color(color);
      const rgb = `${Math.round(c.r * 255)},${Math.round(c.g * 255)},${Math.round(c.b * 255)}`;
      grd.addColorStop(0, `rgba(${rgb},1)`);
      grd.addColorStop(1, `rgba(${rgb},0)`);
      g.save();
      g.translate(x, y);
      g.scale(rx * W, ry * H);
      g.translate(-x, -y);
      g.globalAlpha = a;
      g.fillStyle = grd;
      g.beginPath();
      g.arc(x, y, 1, 0, Math.PI * 2);
      g.fill();
      g.restore();
    };
    // Rubor en pómulos y nariz.
    blob(0.5 - 0.085, 0.36, 0.05, 0.09, C.bubblegum, 0.75);
    blob(0.5 + 0.085, 0.36, 0.05, 0.09, C.bubblegum, 0.75);
    blob(0.5, 0.37, 0.018, 0.04, '#FF7FE3', 0.6);
    // Sombra de ojos ahumada chicle → violeta, escapando hacia fuera (ref-06).
    for (const s of [-1, 1]) {
      blob(0.5 + s * 0.07, 0.53, 0.06, 0.07, C.violet, 0.7);
      blob(0.5 + s * 0.085, 0.545, 0.05, 0.06, C.bubblegum, 0.8);
    }
    const tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    return tex;
  }, []);

export type Variant = 'pink' | 'black';

/** Rojo puntual de la versión negra (ref-16): un ojo y poco más. */
export const RED = '#FF2140';

// --- Entorno: estudio procedural de paneles (reflejos del cromo) ----------
export const useStudioEnvironment = (variant: Variant) => {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  useLayoutEffect(() => {
    const env = new THREE.Scene();
    const bg = variant === 'black' ? '#050505' : '#3A1D58';
    env.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), new THREE.MeshBasicMaterial({ color: bg, side: THREE.BackSide })));
    const panel = (w: number, h: number, color: string, power: number, pos: [number, number, number]) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(power), side: THREE.DoubleSide }));
      m.position.set(...pos);
      m.lookAt(0, 0, 0);
      env.add(m);
    };
    if (variant === 'black') {
      // Cromo negro (ref-17): casi todo el entorno es negro y los reflejos
      // son tiras blancas, duras y de borde nítido. Son lo único que separa
      // un objeto negro de un fondo negro.
      panel(24, 9, '#ffffff', 14, [-8, 22, 12]); // softbox principal arriba-izquierda
      panel(60, 30, '#ffffff', 1.1, [0, 30, -6]); // cenital grande y suave: degradado gris en la parte alta de las esferas
      panel(46, 1.4, '#ffffff', 16, [0, 4, 30]); // tira fina frontal: filo de luz horizontal
      panel(1.6, 40, '#ffffff', 14, [-16, 0, 26]); // tira vertical izquierda
      panel(1.2, 40, '#ffffff', 10, [18, 2, 24]); // tira vertical derecha
      panel(16, 44, '#DDE8FF', 20, [-30, 2, -14]); // contraluz frío izquierda (silueta)
      panel(16, 44, '#DDE8FF', 20, [30, 2, -14]); // contraluz frío derecha (silueta)
      panel(40, 10, '#DDE8FF', 12, [0, 26, -20]); // contraluz cenital trasero: filo de los pinchos de arriba
      panel(30, 6, '#7A7A80', 3, [0, -24, 14]); // rebote gris bajo
      panel(3, 3, RED, 10, [10, -6, 24]); // un único destello rojo
    } else {
      panel(30, 14, '#ffffff', 5, [-6, 22, 14]); // softbox principal arriba-izquierda
      panel(90, 34, C.milk, 2.4, [0, 8, 34]); // relleno amplio detrás de cámara: el cromo lee plata
      panel(70, 16, C.iris, 1.4, [0, -20, 24]); // rebote frontal bajo, lila
      panel(10, 34, C.bubblegum, 4, [28, 2, 6]); // contra chicle a la derecha
      panel(10, 34, C.violet, 5, [-28, 0, 4]); // contra violeta a la izquierda
      panel(40, 2.2, C.milk, 6, [0, 1, 30]); // tira fina: horizonte del cromo
      panel(30, 8, '#3A1060', 2, [0, -24, 10]); // rebote suelo violeta oscuro
      panel(6, 6, C.blood, 3, [12, -10, -20]); // acento sangre por detrás
    }
    const pmrem = new THREE.PMREMGenerator(gl);
    const rt = pmrem.fromScene(env, 0.02);
    scene.environment = rt.texture;
    return () => {
      scene.environment = null;
      rt.dispose();
      pmrem.dispose();
    };
  }, [gl, scene, variant]);
};

// --- Materiales -----------------------------------------------------------
const useMaterials = (skinMap: THREE.Texture, variant: Variant) =>
  useMemo(() => {
    if (variant === 'black') {
      // Metal de albedo muy bajo: refleja solo lo muy brillante → negro con filos blancos.
      const black = new THREE.MeshPhysicalMaterial({ color: '#2A2A2E', metalness: 1, roughness: 0.07, envMapIntensity: 1.3 });
      const silver = new THREE.MeshPhysicalMaterial({ color: '#ffffff', metalness: 1, roughness: 0.08, envMapIntensity: 1 });
      return {
        chrome: silver,
        spike: black,
        skin: black,
        lid: black,
        eye: new THREE.MeshPhysicalMaterial({ color: '#000000', roughness: 0.02, clearcoat: 1, clearcoatRoughness: 0, envMapIntensity: 1.5 }),
        eyeAccent: new THREE.MeshPhysicalMaterial({ color: RED, emissive: new THREE.Color(RED), emissiveIntensity: 0.55, roughness: 0.05, clearcoat: 1, clearcoatRoughness: 0 }),
        lash: black,
        lips: new THREE.MeshPhysicalMaterial({ color: '#1C1C20', metalness: 1, roughness: 0.05, envMapIntensity: 1.5 }),
        mouth: new THREE.MeshBasicMaterial({ color: '#000000' }),
        pearl: silver,
        gem: silver,
        drop: new THREE.MeshPhysicalMaterial({ color: '#ffffff', metalness: 1, roughness: 0.02, envMapIntensity: 1.2 }),
        glint: new THREE.MeshBasicMaterial({ color: '#ffffff' }),
      };
    }
    const chrome = new THREE.MeshPhysicalMaterial({ color: '#ffffff', metalness: 1, roughness: 0.1, envMapIntensity: 1.5 });
    const eye = new THREE.MeshPhysicalMaterial({ color: '#0B0410', roughness: 0.05, clearcoat: 1, clearcoatRoughness: 0, envMapIntensity: 1.6 });
    return {
      chrome,
      spike: chrome,
      eyeAccent: eye,
      skin: new THREE.MeshPhysicalMaterial({
        map: skinMap,
        roughness: 0.32,
        clearcoat: 1,
        clearcoatRoughness: 0.08,
        sheen: 1,
        sheenColor: new THREE.Color(C.bubblegum),
        sheenRoughness: 0.35,
        emissive: new THREE.Color('#2A0024'),
        envMapIntensity: 0.9,
      }),
      lid: new THREE.MeshPhysicalMaterial({ color: '#E2B8F2', roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.1, sheen: 1, sheenColor: new THREE.Color(C.violet) }),
      eye,
      lash: new THREE.MeshPhysicalMaterial({ color: '#12061C', roughness: 0.15, clearcoat: 1, envMapIntensity: 1 }),
      lips: new THREE.MeshPhysicalMaterial({ color: C.bubblegum, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.03, sheen: 0.6, sheenColor: new THREE.Color('#FFB3EE'), envMapIntensity: 1.1 }),
      mouth: new THREE.MeshBasicMaterial({ color: '#1E0838' }),
      pearl: new THREE.MeshPhysicalMaterial({ color: '#FFF1F7', roughness: 0.12, clearcoat: 1, iridescence: 1, iridescenceIOR: 1.6, iridescenceThicknessRange: [200, 700] }),
      gem: new THREE.MeshPhysicalMaterial({ color: C.bubblegum, roughness: 0.05, clearcoat: 1, iridescence: 0.5, envMapIntensity: 1.4 }),
      drop: new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: 0, metalness: 0.3, clearcoat: 1, transparent: true, opacity: 0.22, iridescence: 0.7, envMapIntensity: 2.5 }),
      glint: new THREE.MeshBasicMaterial({ color: '#ffffff' }),
    };
  }, [skinMap, variant]);

/**
 * Cuerno afilado (ref-17): un tubo que sigue una curva y se estrecha hasta
 * acabar en punta. three no trae un tubo de radio variable, así que se barre
 * una circunferencia a lo largo de la curva con los marcos de Frenet.
 */
const hornGeometry = (points: THREE.Vector3[], r0: number, tubular = 96, radial = 32) => {
  const curve = new THREE.CatmullRomCurve3(points);
  const frames = curve.computeFrenetFrames(tubular, false);
  const pos: number[] = [];
  const idx: number[] = [];
  for (let i = 0; i <= tubular; i++) {
    const u = i / tubular;
    const p = curve.getPointAt(u);
    const r = r0 * Math.pow(1 - u, 1.15) + 0.0005;
    const n = frames.normals[i];
    const b = frames.binormals[i];
    for (let j = 0; j <= radial; j++) {
      const v = (j / radial) * Math.PI * 2;
      const cx = -r * Math.cos(v);
      const cy = r * Math.sin(v);
      pos.push(p.x + cx * n.x + cy * b.x, p.y + cx * n.y + cy * b.y, p.z + cx * n.z + cy * b.z);
    }
  }
  for (let i = 0; i < tubular; i++) {
    for (let j = 0; j < radial; j++) {
      const a = i * (radial + 1) + j;
      const c = (i + 1) * (radial + 1) + j;
      idx.push(a, c, a + 1, c, c + 1, a + 1);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
};

const useHorns = () =>
  useMemo(
    () =>
      [-1, 1].map((s) =>
        hornGeometry(
          [
            new THREE.Vector3(0.36 * s, 0.82, 0.32),
            new THREE.Vector3(0.62 * s, 1.35, 0.2),
            new THREE.Vector3(0.86 * s, 1.95, -0.05),
            new THREE.Vector3(0.9 * s, 2.45, -0.25),
            new THREE.Vector3(0.78 * s, 2.85, -0.38),
          ],
          0.2,
        ),
      ),
    [],
  );

/** Párpado: 0 abierto (entornado), 1 cerrado. Un parpadeo por bucle. */
const blinkAmount = (t: number) => {
  const start = 0.64;
  const len = 0.05;
  if (t < start || t > start + len) return 0;
  return Math.sin((Math.PI * (t - start)) / len);
};

export const Head3D: React.FC<{ t: number; variant?: Variant }> = ({ t, variant = 'pink' }) => {
  useStudioEnvironment(variant);
  const headGeo = useHeadGeometry();
  const skinMap = useSkinTexture();
  const m = useMaterials(skinMap, variant);
  const horns = useHorns();
  const black = variant === 'black';

  // Movimiento mínimo y lento: el giro hace que los reflejos barran el cromo.
  const yaw = 0.16 * osc(t);
  const pitch = 0.035 * oscCos(t, 1, 0.1);
  const bob = 0.025 * osc(t, 1, 0.25);
  const blink = blinkAmount(t);
  const lidAngle = -0.12 + (1.35 + 0.12) * blink;

  // Gota del labio: se forma, cae y desaparece (periódica).
  const drop = (() => {
    if (t < 0.55) {
      const g = t / 0.55;
      return { y: -0.9, s: 0.012 + g * 0.042, stretch: 1 + g * 0.6, visible: true };
    }
    const f = (t - 0.55) / 0.3;
    if (f > 1) return { y: 0, s: 0, stretch: 1, visible: false };
    return { y: -0.92 - f * f * 2.4, s: 0.054, stretch: 1.6, visible: true };
  })();

  // En negro los cuernos ocupan la coronilla: los pinchos bajan a los lados (ref-16).
  const spikes = black ? [-118, -96, -74, 74, 96, 118] : [-100, -75, -50, -25, 0, 25, 50, 75, 100];

  return (
    <group position={[0, bob, 0]} rotation={[pitch, yaw, 0]}>
      {/* Cráneo */}
      <mesh geometry={headGeo} material={m.skin} />

      {/* Corona de pinchos cromados (ref-04) */}
      {spikes.map((deg, i) => {
        const a = (deg * Math.PI) / 180;
        const long = black ? Math.abs(deg) === 96 : i % 2 === 0;
        const len = black ? (long ? 0.8 : 0.55) : long ? 0.95 : 0.65;
        const rad = black ? (long ? 0.19 : 0.15) : long ? 0.16 : 0.13;
        const yn = Math.cos(a);
        const r = radiusAt(yn * 0.92) * 0.92;
        const base = new THREE.Vector3(Math.sin(a) * r, yn * HEAD_H * 0.92, -0.12);
        const dir = new THREE.Vector3(Math.sin(a), Math.cos(a) * 1.05, 0).normalize();
        const pos = base.clone().add(dir.clone().multiplyScalar(len / 2 - 0.08));
        return (
          <mesh key={deg} position={pos.toArray()} rotation={[0, 0, -Math.atan2(dir.x, dir.y)]} material={m.spike}>
            <coneGeometry args={[rad, len, 48]} />
          </mesh>
        );
      })}

      {/* Cuernos largos y afilados (ref-17), solo en la versión negra */}
      {black ? horns.map((g, i) => <mesh key={i} geometry={g} material={m.spike} />) : null}

      {/* Ojos */}
      {[-1, 1].map((s) => {
        const p = surf(0.36 * s, 0.06, 0.07);
        return (
          <group key={s} position={p} rotation={[0, 0.32 * s, 0.2 * s]}>
            <mesh scale={[1.45, 0.78, 0.55]} material={s === -1 ? m.eyeAccent : m.eye}>
              <sphereGeometry args={[0.2, 48, 32]} />
            </mesh>
            {/* Brillo duro en el ojo */}
            <mesh position={[0.06 * s, -0.01, 0.108]} material={m.glint}>
              <sphereGeometry args={[0.022, 16, 12]} />
            </mesh>
            {/* Párpado superior: casquete que baja girando sobre x */}
            <mesh scale={[1.5, 0.82, 0.58]} rotation={[lidAngle, 0, 0]} material={m.lid}>
              <sphereGeometry args={[0.2, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2]} />
            </mesh>
            {/* Pestañas en pincho */}
            {[
              [0.3, 0.08, -0.45, 0.5],
              [0.25, 0.14, -0.8, 0.42],
              [0.16, 0.17, -1.1, 0.32],
              [0.3, -0.05, -2.0, 0.3],
            ].map(([x, y, ang, len], i) => (
              <mesh key={i} position={[x * s, y, 0.02]} rotation={[0, 0, ang * s]} material={m.lash}>
                <coneGeometry args={[0.04, len as number, 16]} />
              </mesh>
            ))}
          </group>
        );
      })}

      {/* Piercings de ceja */}
      <mesh position={surf(0.5, 0.36, -0.02)} material={m.chrome}>
        <sphereGeometry args={[0.042, 24, 16]} />
      </mesh>
      <mesh position={surf(0.6, 0.31, -0.02)} material={m.chrome}>
        <sphereGeometry args={[0.032, 24, 16]} />
      </mesh>
      {/* Strass bajo los ojos */}
      {[
        [-0.47, -0.16, 0.03],
        [-0.38, -0.21, 0.024],
        [0.44, -0.19, 0.028],
      ].map(([x, y, r], i) => (
        <mesh key={i} position={surf(x, y, -0.01)} material={i === 1 ? m.pearl : m.chrome}>
          <sphereGeometry args={[r, 20, 14]} />
        </mesh>
      ))}

      {/* Nariz y septum */}
      <mesh position={surf(0, -0.3, 0.06)} scale={[1, 0.8, 0.85]} material={m.skin}>
        <sphereGeometry args={[0.12, 32, 24]} />
      </mesh>
      <mesh position={[0, -0.42, surf(0, -0.42)[2] + 0.04]} rotation={[0.35, 0, 0]} material={m.chrome}>
        <torusGeometry args={[0.055, 0.013, 16, 48, Math.PI * 1.25]} />
      </mesh>

      {/* Boca: hueco, grillz cromados y labios glossy */}
      <group position={[0, -0.66, surf(0, -0.66)[2] - 0.04]}>
        <mesh scale={[1.5, 0.55, 0.4]} material={m.mouth}>
          <sphereGeometry args={[0.2, 32, 16]} />
        </mesh>
        {[-2.5, -1.5, -0.5, 0.5, 1.5, 2.5].map((k) => (
          <mesh key={k} position={[k * 0.06, 0.0, 0.1 - Math.abs(k) * 0.014]} rotation={[0, k * 0.12, 0]} material={m.chrome}>
            <boxGeometry args={[0.054, 0.09, 0.05]} />
          </mesh>
        ))}
        {/* Labio superior en dos lóbulos (arco de cupido). */}
        {[-1, 1].map((k) => (
          <mesh key={k} position={[k * 0.1, 0.1, 0.05]} rotation={[0, 0, -k * 0.18]} scale={[1.0, 0.42, 0.6]} material={m.lips}>
            <sphereGeometry args={[0.17, 48, 32]} />
          </mesh>
        ))}
        <mesh position={[0, -0.13, 0.06]} scale={[1.5, 0.62, 0.72]} material={m.lips}>
          <sphereGeometry args={[0.2, 48, 32]} />
        </mesh>
      </group>

      {/* Gota del labio */}
      {drop.visible ? (
        <mesh position={[0.02, drop.y, surf(0, -0.85)[2] + 0.12]} scale={[1, drop.stretch, 1]} material={m.lips}>
          <sphereGeometry args={[drop.s, 24, 16]} />
        </mesh>
      ) : null}

      {/* Gotas de agua sobre la piel (ref-03) */}
      {[
        [0.3, 0.62, 0.04],
        [0.62, -0.32, 0.04],
        [-0.55, 0.36, 0.03],
      ].map(([x, y, r], i) => (
        <mesh key={i} position={surf(x, y, -r * 0.4)} scale={[1, 1.1, 0.6]} material={m.drop}>
          <sphereGeometry args={[r, 24, 16]} />
        </mesh>
      ))}

      {/* Orejas con aros y perlas (ref-01) */}
      {[-1, 1].map((s) => (
        <group key={s} position={[0.97 * s, -0.02, -0.05]}>
          <mesh scale={[0.32, 0.5, 0.22]} material={m.skin}>
            <sphereGeometry args={[0.5, 32, 24]} />
          </mesh>
          <mesh position={[0.1 * s, 0.12, 0.08]} material={m.pearl}>
            <sphereGeometry args={[0.04, 20, 14]} />
          </mesh>
          <mesh position={[0.12 * s, 0.0, 0.07]} material={m.chrome}>
            <sphereGeometry args={[0.03, 20, 14]} />
          </mesh>
          <group position={[0.04 * s, -0.27, 0.04]} rotation={[0, 0.5 * s, 0]}>
            <mesh material={m.chrome}>
              <torusGeometry args={[0.1, 0.018, 16, 48]} />
            </mesh>
            {s === 1 ? (
              <mesh position={[0, -0.16, 0]} rotation={[0, 0, osc(t) * 0.12]} material={m.gem}>
                <octahedronGeometry args={[0.07, 0]} />
              </mesh>
            ) : null}
          </group>
        </group>
      ))}

      {/* Cuello y gargantilla de pinchos */}
      <mesh position={[0, -1.4, -0.12]} material={m.skin}>
        <cylinderGeometry args={[0.33, 0.4, 0.9, 48]} />
      </mesh>
      <group position={[0, -1.42, -0.12]}>
        <mesh rotation={[Math.PI / 2, 0, 0]} material={m.chrome}>
          <torusGeometry args={[0.37, 0.055, 20, 64]} />
        </mesh>
        {Array.from({ length: 9 }, (_, i) => {
          const a = -1.2 + (i * 2.4) / 8;
          return (
            <mesh key={i} position={[Math.sin(a) * 0.4, -0.1, Math.cos(a) * 0.4]} rotation={[Math.PI + 0.5 * Math.cos(a), 0, -0.5 * Math.sin(a)]} material={m.chrome}>
              <coneGeometry args={[0.035, 0.18, 16]} />
            </mesh>
          );
        })}
      </group>
    </group>
  );
};

/** Perlas (iridiscentes en rosa, cromadas en negro) en órbitas cerradas alrededor de la cabeza. */
export const Pearls: React.FC<{ t: number; variant?: Variant }> = ({ t, variant = 'pink' }) => {
  const mat = useMemo(
    () =>
      variant === 'black'
        ? new THREE.MeshPhysicalMaterial({ color: '#ffffff', metalness: 1, roughness: 0.04, envMapIntensity: 1 })
        : new THREE.MeshPhysicalMaterial({ color: '#FFF1F7', roughness: 0.1, clearcoat: 1, iridescence: 1, iridescenceIOR: 1.7, iridescenceThicknessRange: [150, 750] }),
    [variant],
  );
  const orbs = [
    { r: 0.11, rx: 1.7, ry: 0.5, ph: 0, y: 0.2 },
    { r: 0.08, rx: 1.55, ry: 0.4, ph: 0.4, y: -0.6 },
    { r: 0.06, rx: 1.85, ry: 0.6, ph: 0.7, y: 0.9 },
  ];
  return (
    <>
      {orbs.map((o, i) => {
        const a = 2 * Math.PI * (t + o.ph);
        return (
          <mesh key={i} position={[Math.cos(a) * o.rx, o.y + Math.sin(a * 2) * 0.08, Math.sin(a) * o.ry + 0.3]} material={mat}>
            <sphereGeometry args={[o.r, 32, 24]} />
          </mesh>
        );
      })}
    </>
  );
};
