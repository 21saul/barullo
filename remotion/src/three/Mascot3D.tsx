import React, { useMemo } from 'react';
import * as THREE from 'three';
import { osc, oscCos } from '../lib/tokens';
import { useStudioEnvironment } from './Head3D';

/**
 * Mascota de Barullo (ref-16): bola de cromo negro llena de pinchos, con
 * cascos de DJ, dos cuchillas cromadas por ojos y una sonrisa de dientes
 * blancos. Pensada para leerse por silueta: bola + pinchos + cascos + sonrisa
 * se reconocen aunque sea un icono de 24 px.
 *
 * Unidades: la bola tiene radio 1, centrada en el origen, mirando a +z.
 * `t` = fase 0..1 del bucle; todo es periódico.
 */

const UP = new THREE.Vector3(0, 1, 0);

/** Orientación que lleva +Y a `dir` (los conos de three apuntan a +Y). */
const alignY = (dir: THREE.Vector3) => new THREE.Euler().setFromQuaternion(new THREE.Quaternion().setFromUnitVectors(UP, dir.clone().normalize()));

const useMaterials = () =>
  useMemo(
    () => ({
      // Metal de albedo muy bajo: negro que solo refleja lo muy brillante.
      black: new THREE.MeshPhysicalMaterial({ color: '#2E2E33', metalness: 1, roughness: 0.1, envMapIntensity: 1.5 }),
      // Pinchos en cromo grafito, un punto más claros que la bola: sin esto
      // desaparecen contra el fondo negro en cuanto la mascota se ve pequeña.
      spike: new THREE.MeshPhysicalMaterial({ color: '#5C5C66', metalness: 1, roughness: 0.12, envMapIntensity: 1.6 }),
      silver: new THREE.MeshPhysicalMaterial({ color: '#ffffff', metalness: 1, roughness: 0.05, envMapIntensity: 1 }),
      // Rojo oscuro lacado de los cascos (como en la referencia).
      red: new THREE.MeshPhysicalMaterial({ color: '#7A0A16', roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 1.2 }),
      // Gris claro, no blanco: a tamaño icono los dientes no deben comerse la silueta.
      teeth: new THREE.MeshPhysicalMaterial({ color: '#BFBFC6', roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 0.8 }),
      dial: new THREE.MeshPhysicalMaterial({ color: '#0A0A0A', roughness: 0.3, clearcoat: 1 }),
      dialMark: new THREE.MeshPhysicalMaterial({ color: '#EDEDED', roughness: 0.3, clearcoat: 1 }),
    }),
    [],
  );

/** Pinchos de la bola: direcciones elegidas a mano para dejar libre la cara. */
const SPIKES: Array<[x: number, y: number, z: number, len: number]> = [
  [0, 1, 0.08, 0.78], // coronilla
  [-0.72, 0.62, 0.3, 0.7],
  [0.72, 0.62, 0.3, 0.7],
  [0, 0.58, 0.82, 0.6], // frente
  [-0.82, -0.48, 0.32, 0.62],
  [0.82, -0.48, 0.32, 0.62],
  [0, -0.24, 0.97, 0.42], // entre las cuchillas, apunta abajo (la "nariz")
  [0, 0.45, -0.9, 0.7],
  [-0.62, -0.1, -0.78, 0.66],
  [0.62, -0.1, -0.78, 0.66],
  [0, -0.95, -0.25, 0.6],
  [-0.45, 0.85, -0.3, 0.55],
  [0.45, 0.85, -0.3, 0.55],
];

/** Cuchilla cromada (ojo/gafa). Perfil 2D extruido con bisel. */
const useBladeGeometry = () =>
  useMemo(() => {
    const s = new THREE.Shape();
    s.moveTo(0, 0.11);
    s.quadraticCurveTo(0.55, 0.13, 1.28, 0.42); // filo superior hasta la punta
    s.quadraticCurveTo(0.72, -0.02, 0.12, -0.16); // panza inferior
    s.quadraticCurveTo(-0.02, -0.12, 0, 0.11);
    const g = new THREE.ExtrudeGeometry(s, {
      depth: 0.05,
      bevelEnabled: true,
      bevelThickness: 0.025,
      bevelSize: 0.02,
      bevelSegments: 6,
      curveSegments: 48,
    });
    g.computeVertexNormals();
    return g;
  }, []);

/** Diente: rectángulo redondeado extruido con bisel (cantos suaves, como en ref-16). */
const toothGeometry = (w: number, h: number) => {
  const r = Math.min(w, h) * 0.3;
  const x0 = -w / 2;
  const y0 = -h / 2;
  const s = new THREE.Shape();
  s.moveTo(x0 + r, y0);
  s.lineTo(x0 + w - r, y0);
  s.quadraticCurveTo(x0 + w, y0, x0 + w, y0 + r);
  s.lineTo(x0 + w, y0 + h - r);
  s.quadraticCurveTo(x0 + w, y0 + h, x0 + w - r, y0 + h);
  s.lineTo(x0 + r, y0 + h);
  s.quadraticCurveTo(x0, y0 + h, x0, y0 + h - r);
  s.lineTo(x0, y0 + r);
  s.quadraticCurveTo(x0, y0, x0 + r, y0);
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.04, bevelEnabled: true, bevelThickness: 0.025, bevelSize: 0.012, bevelSegments: 5, curveSegments: 10 });
  g.translate(0, 0, -0.02);
  g.computeVertexNormals();
  return g;
};

export const Mascot3D: React.FC<{ t: number }> = ({ t }) => {
  useStudioEnvironment('black');
  const m = useMaterials();
  const blade = useBladeGeometry();
  const teeth = useMemo(() => {
    const cache = new Map<string, THREE.BufferGeometry>();
    const get = (w: number, h: number) => {
      const k = `${w.toFixed(4)}-${h}`;
      if (!cache.has(k)) cache.set(k, toothGeometry(w, h));
      return cache.get(k)!;
    };
    return { upper: (w: number) => get(w, 0.15), lower: (w: number) => get(w, 0.12) };
  }, []);

  // Giro lento: lo justo para que los reflejos barran el cromo y se vean los cascos.
  const yaw = 0.3 * osc(t);
  const pitch = 0.05 * oscCos(t, 1, 0.15);
  const bob = 0.03 * osc(t, 1, 0.25);
  // Los diales de los cascos giran 1/8 de vuelta por bucle (8 pinchos iguales → sin salto).
  const dialSpin = t * ((Math.PI * 2) / 8);

  // Sonrisa: arco que sube en las comisuras, pegado a la superficie de la bola.
  const smileY = (x: number) => -0.5 + 0.34 * (x / 0.62) ** 2;
  const onSphere = (x: number, y: number, lift = 0) => {
    const z = Math.sqrt(Math.max(0, 1 - x * x - y * y));
    return new THREE.Vector3(x, y, z).multiplyScalar(1 + lift);
  };
  const teethRow = (count: number, y0: number, h: number, span: number) =>
    Array.from({ length: count }, (_, i) => {
      const x = -span + (2 * span * i) / (count - 1);
      const y = smileY(x) + y0;
      const p = onSphere(x, y, -0.015);
      const w = ((2 * span) / (count - 1)) * 0.9;
      return { p, rot: new THREE.Euler().setFromQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), p.clone().normalize())), h, w };
    });

  return (
    <group position={[0, bob, 0]} rotation={[pitch, yaw, 0]}>
      {/* Bola */}
      <mesh material={m.black}>
        <sphereGeometry args={[1, 160, 120]} />
      </mesh>

      {/* Pinchos negros */}
      {SPIKES.map(([x, y, z, len], i) => {
        const dir = new THREE.Vector3(x, y, z).normalize();
        const pos = dir.clone().multiplyScalar(0.92 + len / 2);
        return (
          <mesh key={i} position={pos.toArray()} rotation={alignY(dir)} material={m.spike}>
            <coneGeometry args={[len * 0.32, len, 64, 1]} />
          </mesh>
        );
      })}

      {/* Cuchillas cromadas por ojos, una en espejo de la otra. Flotan delante
          de la bola como unas gafas: una pieza plana pegada a la esfera la cortaría. */}
      {[-1, 1].map((s) => (
        <group key={s} position={[0.05 * s, -0.1, 1.07]} rotation={[0, 0.28 * s, 0]} scale={[s, 1, 1]}>
          <mesh geometry={blade} material={m.silver} />
        </group>
      ))}

      {/* Sonrisa: fila superior y fila inferior de dientes blancos */}
      {[...teethRow(11, 0, 0.15, 0.54), ...teethRow(10, -0.145, 0.12, 0.47)].map(({ p, rot, h, w }, i) => (
        <mesh key={i} position={p.toArray()} rotation={rot} geometry={h > 0.13 ? teeth.upper(w) : teeth.lower(w)} material={m.teeth} />
      ))}

      {/* Cascos de DJ */}
      <group>
        {/* Diadema: aro cromado + banda roja, con pinchitos plateados */}
        <mesh rotation={[0, 0, 0]} material={m.silver}>
          <torusGeometry args={[1.2, 0.035, 16, 128, Math.PI]} />
        </mesh>
        <mesh position={[0, 0, -0.06]} material={m.red}>
          <torusGeometry args={[1.12, 0.05, 16, 128, Math.PI]} />
        </mesh>
        {Array.from({ length: 7 }, (_, i) => {
          const a = 0.32 + (i * (Math.PI - 0.64)) / 6;
          const dir = new THREE.Vector3(Math.cos(a), Math.sin(a), 0);
          return (
            <mesh key={i} position={dir.clone().multiplyScalar(1.28).toArray()} rotation={alignY(dir)} material={m.silver}>
              <coneGeometry args={[0.045, 0.18, 24]} />
            </mesh>
          );
        })}
        {/* Copas */}
        {[-1, 1].map((s) => (
          <group key={s} position={[1.0 * s, -0.02, 0]} rotation={[0, 0, (s * Math.PI) / 2]}>
            <mesh material={m.red}>
              <cylinderGeometry args={[0.46, 0.46, 0.3, 96]} />
            </mesh>
            <group position={[0, -0.16 * s, 0]} rotation={[0, dialSpin * s, 0]}>
              {/* Aro en el plano del dial (eje Y): así el giro del dial es simétrico y el bucle cierra. */}
              <mesh rotation={[Math.PI / 2, 0, 0]} material={m.silver}>
                <torusGeometry args={[0.4, 0.04, 16, 96]} />
              </mesh>
              <mesh rotation={[Math.PI / 2, 0, 0]} material={m.dial}>
                <circleGeometry args={[0.38, 96]} />
              </mesh>
              {/* Marcas del dial (como en ref-16) y pincho central */}
              {Array.from({ length: 8 }, (_, i) => {
                const a = (i * Math.PI * 2) / 8;
                return (
                  <mesh key={i} position={[Math.cos(a) * 0.27, -0.01 * s, Math.sin(a) * 0.27]} rotation={[0, -a, 0]} material={m.dialMark}>
                    <boxGeometry args={[0.1, 0.02, 0.05]} />
                  </mesh>
                );
              })}
              <mesh position={[0, -0.18 * s, 0]} rotation={[s === 1 ? Math.PI : 0, 0, 0]} material={m.silver}>
                <coneGeometry args={[0.09, 0.36, 48]} />
              </mesh>
              {/* Pinchitos alrededor de la copa */}
              {Array.from({ length: 8 }, (_, i) => {
                const a = (i * Math.PI * 2) / 8 + Math.PI / 8;
                const dir = new THREE.Vector3(Math.cos(a), 0, Math.sin(a));
                return (
                  <mesh key={i} position={dir.clone().multiplyScalar(0.53).toArray()} rotation={alignY(dir)} material={m.silver}>
                    <coneGeometry args={[0.04, 0.16, 24]} />
                  </mesh>
                );
              })}
            </group>
          </group>
        ))}
      </group>
    </group>
  );
};
