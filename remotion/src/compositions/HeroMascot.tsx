import { ThreeCanvas } from '@remotion/three';
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import * as THREE from 'three';
import { SparkleField } from '../components/Art';
import { Mascot3D } from '../three/Mascot3D';

export const MASCOT_SECONDS = 8;

/** Fondo de la web: el vídeo tiene que fundirse con él sin costura. */
export const WEB_BLACK = '#050505';

const FOV = 24;
/** Alto visible en unidades 3D: la mascota con pinchos llena casi todo el alto. */
const VISIBLE_H = 3.78;

/**
 * Héroe con la mascota de Barullo, a sangre: fondo #050505 plano (sin viñeta
 * ni halo) para que no se vea el borde del vídeo contra la página.
 * Supersampling (dpr 2): el canvas se pinta al doble y Chrome lo reduce, así
 * los filos del cromo salen limpios con el render por software.
 */
export const HeroMascot: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;
  const camZ = VISIBLE_H / 2 / Math.tan((FOV * Math.PI) / 360);
  const unit = height / 1080;
  const cx = width / 2;
  const half = height * 0.5;

  const sparkles: Array<[number, number, number]> = [
    [cx - half * 0.86, height * 0.16, 34],
    [cx + half * 0.84, height * 0.84, 30],
    [cx + half * 0.9, height * 0.2, 22],
    [cx - half * 0.9, height * 0.8, 24],
  ].map(([x, y, s]) => [x, y, s * unit]);

  return (
    <AbsoluteFill style={{ background: WEB_BLACK }}>
      <ThreeCanvas
        width={width}
        height={height}
        dpr={2}
        camera={{ fov: FOV, position: [0, 0.08, camZ], near: 0.1, far: 100 }}
        gl={{ antialias: true, alpha: true, preserveDrawingBuffer: true }}
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.NeutralToneMapping;
          gl.toneMappingExposure = 1;
          // Canvas transparente: el #050505 lo pone el CSS, exacto, sin pasar por el tone mapping.
          gl.setClearColor(0x000000, 0);
        }}
      >
        <directionalLight position={[-3, 4, 5]} intensity={1.2} color="#ffffff" />
        {/* Contraluces fríos: dibujan la silueta contra el negro. */}
        <directionalLight position={[5, 2, -3]} intensity={3.2} color="#DDE8FF" />
        <directionalLight position={[-5, 1.5, -3]} intensity={3.2} color="#DDE8FF" />
        <Mascot3D t={t} />
      </ThreeCanvas>
      <SparkleField t={t} points={sparkles} seed={41} mono />
    </AbsoluteFill>
  );
};
