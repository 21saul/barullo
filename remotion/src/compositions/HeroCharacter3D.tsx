import { ThreeCanvas } from '@remotion/three';
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import * as THREE from 'three';
import { Backdrop, Bloom, SparkleField } from '../components/Art';
import { C } from '../lib/tokens';
import { Head3D, Pearls, Variant } from '../three/Head3D';

export const CHARACTER3D_SECONDS = 8;

/** Fondo de la web en la versión negra. */
const WEB_BLACK = '#050505';

const FOV = 26;

/**
 * Encuadre por variante: alto visible en unidades 3D y desplazamiento de la
 * cabeza. La negra tiene cuernos, así que necesita más alto.
 */
const FRAMING: Record<Variant, { visibleH: number; offsetY: number }> = {
  pink: { visibleH: 4.05, offsetY: 0 },
  black: { visibleH: 4.75, offsetY: -0.62 },
};

/**
 * Héroe con personaje en 3D real. Fondo y destellos son 2D; la cabeza es
 * three.js renderizado por software (swangle).
 * - `black` (actual): cromo negro acromático, filos blancos duros, un ojo rojo.
 * - `pink`: versión hyperpop chicle/violeta anterior.
 */
export const HeroCharacter3D: React.FC<{ variant: Variant }> = ({ variant }) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;
  const unit = height / 720;
  const cx = width / 2;
  const headW = height * 0.62;
  const black = variant === 'black';
  const { visibleH, offsetY } = FRAMING[variant];
  const camZ = visibleH / 2 / Math.tan((FOV * Math.PI) / 360);
  const ground = black ? WEB_BLACK : C.void;

  const sparkles: Array<[number, number, number]> = [
    [cx - headW * 0.85, height * 0.2, 30],
    [cx + headW * 0.8, height * 0.28, 38],
    [cx - headW * 0.75, height * 0.74, 24],
    [cx + headW * 0.9, height * 0.8, 28],
    [cx + headW * 1.3, height * 0.12, 20],
    [cx - headW * 1.3, height * 0.5, 20],
  ].map(([x, y, s]) => [x, y, s * unit]);

  return (
    <AbsoluteFill style={{ background: ground }}>
      {black ? (
        // Viñeta gris muy leve: da aire a la silueta sin colorear nada.
        <AbsoluteFill style={{ background: `radial-gradient(60% 70% at 50% 42%, #1A1A1D 0%, ${WEB_BLACK} 70%)` }} />
      ) : (
        <>
          <Backdrop cy={45} />
          <Bloom t={t} x={cx} y={height * 0.42} radius={headW * 0.9} intensity={0.85} />
        </>
      )}
      <ThreeCanvas
        width={width}
        height={height}
        camera={{ fov: FOV, position: [0, 0.1, camZ], near: 0.1, far: 100 }}
        gl={{ antialias: true, alpha: true, preserveDrawingBuffer: true }}
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.NeutralToneMapping;
          gl.toneMappingExposure = 1.05;
          gl.setClearColor(0x000000, 0);
        }}
      >
        {black ? (
          <>
            <directionalLight position={[-3, 4, 5]} intensity={1.4} color="#ffffff" />
            {/* Contraluces fríos: dibujan la silueta contra el negro. */}
            <directionalLight position={[5, 1.5, -3]} intensity={3} color="#DDE8FF" />
            <directionalLight position={[-5, 1, -3]} intensity={3} color="#DDE8FF" />
          </>
        ) : (
          <>
            <directionalLight position={[-3, 4, 5]} intensity={1.6} color="#ffffff" />
            <directionalLight position={[5, 0.5, -2]} intensity={2.2} color={C.bubblegum} />
            <directionalLight position={[-5, -1, -2]} intensity={2.4} color={C.violet} />
            <ambientLight intensity={0.25} color={C.iris} />
          </>
        )}
        <group position={[0, offsetY, 0]}>
          <Head3D t={t} variant={variant} />
          <Pearls t={t} variant={variant} />
        </group>
      </ThreeCanvas>
      {/* El cuello se funde con el fondo: el busto no termina en un corte seco. */}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 84%, ${ground}D9 96%, ${ground} 100%)` }} />
      <SparkleField t={t} points={sparkles} seed={31} mono={black} />
    </AbsoluteFill>
  );
};
