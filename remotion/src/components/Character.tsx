import React from 'react';
import { C, osc, oscCos, pulse, twinkle } from '../lib/tokens';
import { useSvgId } from '../lib/useSvgId';

/**
 * Retrato hyperpop frontal, ilustración vectorial (no imitación de render 3D).
 * Lenguaje de las referencias: cráneo glossy con subsurface rosa, ojos
 * entornados negros con pestañas en pincho (ref-02), grillz cromados
 * (ref-12, ref-15), corona de pinchos (ref-04), piercings y perlas (ref-01),
 * gotas de agua sobre la piel (ref-03).
 *
 * Coordenadas en un lienzo de 1000×1100. La cabeza no se mueve: solo se animan
 * piezas locales (reflejo, párpados, gotas, destellos). Así el vídeo pesa poco
 * y nada distrae del contenido que va encima.
 *
 * `t` = fase 0..1 del bucle. Todo es periódico: t=0 y t=1 dan el mismo dibujo.
 */
export const CHARACTER_VIEWBOX = { width: 1000, height: 1100 };

const HEAD =
  'M 500 140 C 690 140 820 280 815 470 C 812 600 760 700 680 790 C 620 855 560 882 500 882 C 440 882 380 855 320 790 C 240 700 188 600 185 470 C 180 280 310 140 500 140 Z';

const EYE = 'M 272 552 C 304 494 428 476 484 520 C 450 582 330 598 272 552 Z';

/** Párpado: 0 = abierto (entornado, como en las referencias), 1 = cerrado. */
const blinkAmount = (t: number) => {
  const start = 0.64;
  const len = 0.055;
  if (t < start || t > start + len) return 0;
  return Math.sin((Math.PI * (t - start)) / len);
};

/** Banda de luz que barre todo el cromo una vez por bucle y descansa. */
const sweepX = (t: number) => {
  const s = Math.min(1, Math.max(0, (t - 0.08) / 0.5));
  return -400 + s * 1800;
};

export const Character: React.FC<{
  t: number;
  width: number;
  height: number;
  /** Franja vertical visible del lienzo [y0, alto]; por defecto entero. */
  crop?: [number, number];
  style?: React.CSSProperties;
}> = ({ t, width, height, crop = [0, CHARACTER_VIEWBOX.height], style }) => {
  const id = useSvgId('char');
  const u = (name: string) => `url(#${id}-${name})`;
  const sx = sweepX(t);
  const blink = blinkAmount(t);

  /** Pieza cromada: gradiente fijo + banda de barrido encima. */
  const Chrome: React.FC<{ d: string; grad?: 'h' | 'v'; sw?: number }> = ({ d, grad = 'v', sw = 3 }) => (
    <>
      <path d={d} fill={u(grad === 'h' ? 'chromeH' : 'chromeV')} stroke="#1A0C26" strokeWidth={sw} strokeLinejoin="round" />
      <path d={d} fill={u('sweep')} style={{ mixBlendMode: 'screen' }} />
    </>
  );

  const ChromeBall: React.FC<{ cx: number; cy: number; r: number; pearl?: boolean }> = ({ cx, cy, r, pearl }) => (
    <g>
      <circle cx={cx} cy={cy} r={r} fill={u(pearl ? 'pearl' : 'ball')} stroke="#1A0C26" strokeWidth={1.5} />
      <circle cx={cx} cy={cy} r={r} fill={u('sweep')} style={{ mixBlendMode: 'screen' }} />
      <ellipse cx={cx - r * 0.35} cy={cy - r * 0.4} rx={r * 0.32} ry={r * 0.2} fill="#fff" transform={`rotate(-30 ${cx - r * 0.35} ${cy - r * 0.4})`} />
    </g>
  );

  const Ring: React.FC<{ cx: number; cy: number; r: number; w: number; from: number; to: number }> = ({ cx, cy, r, w, from, to }) => {
    const a0 = (from * Math.PI) / 180;
    const a1 = (to * Math.PI) / 180;
    const d = `M ${cx + r * Math.cos(a0)} ${cy + r * Math.sin(a0)} A ${r} ${r} 0 ${to - from > 180 ? 1 : 0} 1 ${cx + r * Math.cos(a1)} ${cy + r * Math.sin(a1)}`;
    return (
      <g fill="none" strokeLinecap="round">
        <path d={d} stroke="#1A0C26" strokeWidth={w + 4} />
        <path d={d} stroke={u('chromeV')} strokeWidth={w} />
        <path d={d} stroke={u('sweep')} strokeWidth={w} style={{ mixBlendMode: 'screen' }} />
        <path d={d} stroke="#fff" strokeWidth={w * 0.25} opacity={0.8} strokeDasharray={`${r * 0.6} ${r * 6}`} />
      </g>
    );
  };

  /** Gota de agua transparente (ref-03): solo bordes y brillo. */
  const Droplet: React.FC<{ cx: number; cy: number; r: number; glint?: number }> = ({ cx, cy, r, glint = 0 }) => (
    <g>
      <ellipse cx={cx} cy={cy + r * 0.12} rx={r} ry={r * 1.08} fill={u('drop')} />
      <path
        d={`M ${cx - r * 0.85} ${cy + r * 0.3} A ${r * 0.9} ${r * 0.9} 0 0 0 ${cx + r * 0.85} ${cy + r * 0.3}`}
        fill="none"
        stroke="#4A1E7A"
        strokeOpacity={0.55}
        strokeWidth={r * 0.18}
      />
      <ellipse cx={cx - r * 0.32} cy={cy - r * 0.35} rx={r * 0.28} ry={r * 0.2} fill="#fff" opacity={0.9 + glint * 0.1} />
      {glint > 0.05 ? <circle cx={cx - r * 0.32} cy={cy - r * 0.35} r={r * (0.4 + glint * 0.9)} fill="#fff" opacity={glint * 0.5} filter={u('soft')} /> : null}
    </g>
  );

  /** Ojo izquierdo; el derecho es su espejo. */
  const Eye: React.FC<{ side: 'l' | 'r' }> = ({ side }) => {
    // Línea del párpado superior: entornado por defecto, baja al parpadear.
    const lidTop = 460;
    const lidOpen = 520;
    const lidClosed = 588;
    const lid = lidOpen + (lidClosed - lidOpen) * blink;
    const lidPath = `M 260 ${lidTop} L 495 ${lidTop} L 495 ${lid - 14} C 440 ${lid - 2} 350 ${lid + 6} 262 ${lid + 30} Z`;
    const lidEdge = `M 274 ${lid + 26} C 350 ${lid + 5} 440 ${lid - 3} 486 ${lid - 12}`;
    const sparkle = twinkle(t, 1, side === 'l' ? 0.1 : 0.45, 5);
    return (
      <g>
        {/* Sombra ahumada chicle→violeta que se escapa hacia fuera (ref-06). */}
        <ellipse cx={350} cy={526} rx={160} ry={78} fill={u('shadow')} filter={u('blur')} transform="rotate(-14 350 526)" />
        <ellipse cx={300} cy={540} rx={90} ry={36} fill={C.bubblegum} opacity={0.55} filter={u('blur')} transform="rotate(-24 300 540)" />
        <g clipPath={u('eyeClip')}>
          <path d={EYE} fill={u('eyeball')} />
          {/* Reflejo violeta inferior y brillo duro: ojo negro glossy. */}
          <ellipse cx={380} cy={578} rx={90} ry={16} fill={C.violet} opacity={0.7} filter={u('soft')} />
          <ellipse cx={420} cy={540} rx={17} ry={12} fill="#fff" />
          <circle cx={392} cy={556} r={5} fill="#fff" opacity={0.85} />
          <path d={lidPath} fill={u('lid')} />
          <path d={lidEdge} fill="none" stroke="#12061C" strokeWidth={7} strokeLinecap="round" />
        </g>
        <path d={EYE} fill="none" stroke="#12061C" strokeWidth={3} />
        {/* Con el ojo cerrado, la línea de pestañas queda fuera del recorte: se pinta aparte. */}
        {blink > 0.3 ? (
          <path d="M 276 556 C 340 590 430 584 482 524" fill="none" stroke="#12061C" strokeWidth={7} strokeLinecap="round" opacity={Math.min(1, (blink - 0.3) * 2.5)} />
        ) : null}
        {/* Delineado en ala y pestañas en pincho gruesas y brillantes (ref-02). */}
        <path d="M 278 548 C 250 530 226 508 200 476 C 240 500 270 518 296 530 Z" fill="#12061C" />
        {[
          [292, 530, 190, 440, 20],
          [322, 512, 252, 410, 18],
          [360, 500, 330, 404, 15],
          [282, 566, 196, 590, 15],
        ].map(([x1, y1, x2, y2, w], i) => {
          const dx = x2 - x1;
          const dy = y2 - y1;
          const len = Math.hypot(dx, dy);
          const nx = (-dy / len) * (w / 2);
          const ny = (dx / len) * (w / 2);
          const mx = x1 + dx * 0.55 + nx * 0.6;
          const my = y1 + dy * 0.55 + ny * 0.6;
          return (
            <g key={i}>
              <path d={`M ${x1 - nx} ${y1 - ny} Q ${mx} ${my} ${x2} ${y2} Q ${mx + nx * 0.4} ${my + ny * 0.4} ${x1 + nx} ${y1 + ny} Z`} fill="#12061C" />
              <path d={`M ${x1 + dx * 0.15} ${y1 + dy * 0.15} Q ${mx} ${my} ${x1 + dx * 0.7} ${y1 + dy * 0.7}`} stroke="#8E5AD9" strokeWidth={2.5} fill="none" opacity={0.8} />
            </g>
          );
        })}
        {/* Destello dentro del ojo (ref-05). */}
        {sparkle > 0.02 ? (
          <path
            transform={`translate(410 548) scale(${10 + sparkle * 16})`}
            d="M0,-1 C0.1,-0.1 0.1,-0.1 1,0 C0.1,0.1 0.1,0.1 0,1 C-0.1,0.1 -0.1,0.1 -1,0 C-0.1,-0.1 -0.1,-0.1 0,-1 Z"
            fill={C.milk}
            opacity={sparkle * (1 - blink)}
          />
        ) : null}
        {/* Strass bajo el ojo. */}
        {[
          [312, 622, 8],
          [340, 640, 6],
          [290, 642, 5],
        ].map(([x, y, r], i) => (
          <ChromeBall key={i} cx={x} cy={y} r={r} pearl={i === 1} />
        ))}
      </g>
    );
  };

  // Gota que se forma en el labio inferior, cae y desaparece.
  const lipDrop = (() => {
    const grow = Math.min(1, t / 0.55);
    if (t < 0.55) return { y: 846 + grow * 10, r: 2 + grow * 9, stretch: 1 + grow * 0.5, o: grow };
    const f = (t - 0.55) / 0.3;
    if (f > 1) return null;
    return { y: 856 + f * f * 420, r: 11, stretch: 1.6, o: 1 - Math.max(0, f - 0.7) / 0.3 };
  })();

  // Lágrima: baja por la mejilla izquierda y se desvanece.
  const tear = (() => {
    const s = (t - 0.18) / 0.6;
    if (s < 0 || s > 1) return null;
    const ease = s * s * (3 - 2 * s);
    return { y: 590 + ease * 190, x: 312 - ease * 14, o: Math.sin(Math.PI * s) };
  })();

  const headHi = { x: 430 + osc(t) * 8, y: 290 + oscCos(t) * 5 };

  return (
    <svg width={width} height={height} viewBox={`0 ${crop[0]} ${CHARACTER_VIEWBOX.width} ${crop[1]}`} style={style}>
      <defs>
        <linearGradient id={`${id}-chromeH`} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#3A3150" />
          <stop offset="0.28" stopColor={C.chrome3} />
          <stop offset="0.46" stopColor={C.chrome1} />
          <stop offset="0.6" stopColor={C.chrome2} />
          <stop offset="0.82" stopColor="#5B4F78" />
          <stop offset="1" stopColor="#FFB8EE" />
        </linearGradient>
        <linearGradient id={`${id}-chromeV`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor={C.chrome1} />
          <stop offset="0.38" stopColor={C.chrome2} />
          <stop offset="0.5" stopColor={C.chrome3} />
          <stop offset="0.53" stopColor="#2E2145" />
          <stop offset="0.66" stopColor="#B07BE8" />
          <stop offset="0.85" stopColor="#FFC4F0" />
          <stop offset="1" stopColor={C.chrome2} />
        </linearGradient>
        <linearGradient id={`${id}-sweep`} gradientUnits="userSpaceOnUse" x1={sx - 160} y1={0} x2={sx + 160} y2={260}>
          <stop offset="0" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.44" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.5" stopColor="#fff" stopOpacity="0.9" />
          <stop offset="0.56" stopColor={C.bubblegum} stopOpacity="0.3" />
          <stop offset="0.62" stopColor="#fff" stopOpacity="0" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <radialGradient id={`${id}-skin`} cx="0.42" cy="0.32" r="0.78">
          <stop offset="0" stopColor={C.milk} />
          <stop offset="0.34" stopColor="#F4DCF4" />
          <stop offset="0.62" stopColor="#D2B8F2" />
          <stop offset="0.84" stopColor="#9C78E6" />
          <stop offset="1" stopColor="#4B1FA0" />
        </radialGradient>
        <radialGradient id={`${id}-ear`} cx="0.6" cy="0.4" r="0.7">
          <stop offset="0" stopColor="#F4DCF4" />
          <stop offset="0.6" stopColor="#C9A6F0" />
          <stop offset="1" stopColor="#6A35C8" />
        </radialGradient>
        <radialGradient id={`${id}-blush`}>
          <stop offset="0" stopColor={C.bubblegum} stopOpacity="0.75" />
          <stop offset="1" stopColor={C.bubblegum} stopOpacity="0" />
        </radialGradient>
        <radialGradient id={`${id}-shadow`}>
          <stop offset="0" stopColor="#B21CA0" stopOpacity="0.9" />
          <stop offset="0.55" stopColor={C.violet} stopOpacity="0.55" />
          <stop offset="1" stopColor={C.violet} stopOpacity="0" />
        </radialGradient>
        <radialGradient id={`${id}-eyeball`} cx="0.55" cy="0.4" r="0.7">
          <stop offset="0" stopColor="#3B1670" />
          <stop offset="0.6" stopColor="#14061F" />
          <stop offset="1" stopColor={C.void} />
        </radialGradient>
        <linearGradient id={`${id}-lid`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="#E9CDF2" />
          <stop offset="1" stopColor="#C493E8" />
        </linearGradient>
        <linearGradient id={`${id}-lips`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="#FF8FE6" />
          <stop offset="0.45" stopColor={C.bubblegum} />
          <stop offset="1" stopColor="#9E0F7C" />
        </linearGradient>
        <linearGradient id={`${id}-lipsTop`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="#C21C9E" />
          <stop offset="1" stopColor="#FF6BDF" />
        </linearGradient>
        <radialGradient id={`${id}-ball`} cx="0.35" cy="0.3" r="0.8">
          <stop offset="0" stopColor={C.chrome1} />
          <stop offset="0.45" stopColor={C.chrome2} />
          <stop offset="0.8" stopColor={C.chrome3} />
          <stop offset="1" stopColor="#2E2145" />
        </radialGradient>
        <radialGradient id={`${id}-pearl`} cx="0.35" cy="0.3" r="0.8">
          <stop offset="0" stopColor="#fff" />
          <stop offset="0.6" stopColor="#F3E4F7" />
          <stop offset="1" stopColor={C.iris} />
        </radialGradient>
        <radialGradient id={`${id}-drop`} cx="0.4" cy="0.35" r="0.7">
          <stop offset="0" stopColor="#fff" stopOpacity="0.15" />
          <stop offset="0.7" stopColor="#fff" stopOpacity="0.05" />
          <stop offset="1" stopColor={C.iris} stopOpacity="0.6" />
        </radialGradient>
        <radialGradient id={`${id}-heart`} cx="0.35" cy="0.3" r="0.8">
          <stop offset="0" stopColor="#FFD0F4" />
          <stop offset="0.45" stopColor={C.bubblegum} />
          <stop offset="1" stopColor="#7A0A5E" />
        </radialGradient>
        <clipPath id={`${id}-head`}>
          <path d={HEAD} />
        </clipPath>
        <clipPath id={`${id}-eyeClip`}>
          <path d={EYE} />
        </clipPath>
        <clipPath id={`${id}-mouth`}>
          <path d="M 408 742 C 450 748 550 748 592 742 C 562 784 438 784 408 742 Z" />
        </clipPath>
        <filter id={`${id}-blur`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="16" />
        </filter>
        <filter id={`${id}-soft`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="5" />
        </filter>
        <filter id={`${id}-rim`} x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur stdDeviation="10" />
        </filter>
      </defs>

      {/* Corona de pinchos detrás del cráneo (ref-04). Fija: solo barre la luz. */}
      <g>
        {[-104, -78, -52, -26, 0, 26, 52, 78, 104].map((a, i) => {
          const len = i % 2 === 0 ? 270 : 190;
          const w = i % 2 === 0 ? 104 : 84;
          const inner = 255;
          const d = `M ${-w / 2} ${-inner} C ${-w * 0.42} ${-inner - len * 0.45} ${-w * 0.08} ${-inner - len * 0.85} 0 ${-inner - len} C ${w * 0.08} ${-inner - len * 0.85} ${w * 0.42} ${-inner - len * 0.45} ${w / 2} ${-inner} Z`;
          return (
            <g key={a} transform={`translate(500 490) rotate(${a})`}>
              <Chrome d={d} grad="h" />
            </g>
          );
        })}
      </g>

      {/* Cuello, hombros y gargantilla de pinchos. */}
      <path d="M 405 790 L 392 1100 L 608 1100 L 595 790 Z" fill="#8F68E0" />
      <path d="M 405 820 C 450 860 550 860 595 820 L 600 900 C 550 930 450 930 400 900 Z" fill="#5B2BB8" opacity={0.7} />
      <path d="M 398 990 C 290 1010 170 1040 70 1100 L 930 1100 C 830 1040 710 1010 602 990 Z" fill={u('skin')} opacity={0.9} />
      <g>
        <Chrome d="M 388 950 C 450 972 550 972 612 950 L 614 984 C 552 1006 448 1006 386 984 Z" />
        {[410, 445, 482, 518, 555, 590].map((x, i) => {
          const y = 990 + (i === 0 || i === 5 ? -4 : 4);
          return <Chrome key={x} d={`M ${x - 12} ${y} L ${x} ${y + 40} L ${x + 12} ${y} Z`} grad="h" sw={2} />;
        })}
      </g>

      {/* Orejas con piercings (ref-01). */}
      {(['l', 'r'] as const).map((side) => (
        <g key={side} transform={side === 'r' ? 'translate(1000 0) scale(-1 1)' : undefined}>
          <ellipse cx={192} cy={520} rx={58} ry={92} fill={u('ear')} stroke="#4B1FA0" strokeWidth={2} />
          <path d="M 205 470 C 170 480 168 560 200 580" fill="none" stroke="#7B4BD0" strokeWidth={10} strokeLinecap="round" opacity={0.6} />
          <ChromeBall cx={170} cy={470} r={9} />
          <ChromeBall cx={160} cy={500} r={7} pearl />
          <Ring cx={186} cy={612} r={26} w={7} from={-60} to={250} />
        </g>
      ))}
      {/* Pendiente de corazón chicle colgando del aro derecho. */}
      <g transform={`rotate(${osc(t) * 4} 814 636)`}>
        <path d="M 814 636 L 814 664" stroke={C.chrome2} strokeWidth={3} />
        <path
          d="M 814 712 C 790 696 776 684 776 668 C 776 656 786 648 797 648 C 805 648 811 653 814 659 C 817 653 823 648 831 648 C 842 648 852 656 852 668 C 852 684 838 696 814 712 Z"
          fill={u('heart')}
          stroke="#1A0C26"
          strokeWidth={2}
        />
        <ellipse cx={796} cy={662} rx={7} ry={4} fill="#fff" transform="rotate(-30 796 662)" />
      </g>

      {/* Cabeza: base, subsurface, borde de luz y brillos. */}
      <path d={HEAD} fill={u('skin')} />
      <g clipPath={u('head')}>
        <ellipse cx={335} cy={668} rx={120} ry={74} fill={u('blush')} />
        <ellipse cx={665} cy={668} rx={120} ry={74} fill={u('blush')} />
        <ellipse cx={500} cy={140} rx={200} ry={60} fill={C.bubblegum} opacity={0.18} filter={u('blur')} />
        <path d={HEAD} fill="none" stroke="#2A0D5C" strokeWidth={70} opacity={0.55} filter={u('blur')} />
        <path d={HEAD} fill="none" stroke={C.bubblegum} strokeWidth={30} opacity={0.9} filter={u('rim')} transform="translate(-16 8)" />
        <path d={HEAD} fill="none" stroke={C.violet} strokeWidth={46} opacity={0.9} filter={u('rim')} transform="translate(18 -6)" />
        <ellipse cx={500} cy={880} rx={170} ry={60} fill="#4B1FA0" opacity={0.45} filter={u('blur')} />
        {/* Especular: blando en la frente, duros en pómulos, nariz y barbilla. */}
        <ellipse cx={headHi.x} cy={headHi.y} rx={120} ry={56} fill="#fff" opacity={0.75} filter={u('soft')} transform={`rotate(-18 ${headHi.x} ${headHi.y})`} />
        <ellipse cx={headHi.x + 150} cy={headHi.y - 30} rx={26} ry={12} fill="#fff" opacity={0.9} transform={`rotate(20 ${headHi.x + 150} ${headHi.y - 30})`} />
        <ellipse cx={270} cy={612} rx={34} ry={14} fill="#fff" opacity={0.6} filter={u('soft')} transform="rotate(-40 270 612)" />
        <ellipse cx={738} cy={600} rx={20} ry={9} fill="#fff" opacity={0.7} transform="rotate(40 738 600)" />
        <ellipse cx={500} cy={850} rx={36} ry={10} fill="#fff" opacity={0.55} filter={u('soft')} />
      </g>
      <path d={HEAD} fill="none" stroke="#2A0D5C" strokeWidth={3} opacity={0.6} />

      {/* Piercings de ceja (ref-04). */}
      <ChromeBall cx={662} cy={452} r={9} />
      <ChromeBall cx={692} cy={438} r={7} />

      {/* Ojos. */}
      <Eye side="l" />
      <g transform="translate(1000 0) scale(-1 1)">
        <Eye side="r" />
      </g>

      {/* Nariz con septum cromado. */}
      <g transform="translate(500 640) scale(1.3) translate(-500 -640)">
      <path d="M 486 560 C 482 600 476 630 470 650" fill="none" stroke="#B48BEA" strokeWidth={6} strokeLinecap="round" opacity={0.6} />
      <ellipse cx={500} cy={642} rx={34} ry={20} fill="#E7C9F4" />
      <ellipse cx={494} cy={634} rx={12} ry={6} fill="#fff" opacity={0.85} />
      <ellipse cx={482} cy={656} rx={9} ry={5} fill="#3B1670" />
      <ellipse cx={518} cy={656} rx={9} ry={5} fill="#3B1670" />
      <Ring cx={500} cy={668} r={15} w={6} from={10} to={170} />
      </g>

      {/* Boca: labios glossy, hueco oscuro y grillz cromados. */}
      <g transform="translate(500 760) scale(1.3) translate(-500 -760)">
      <path d="M 408 742 C 450 748 550 748 592 742 C 562 784 438 784 408 742 Z" fill="#1E0838" />
      <g clipPath={u('mouth')}>
        {[440, 466, 488, 512, 534, 560].map((x, i) => (
          <g key={x}>
            <rect x={x - 11} y={736} width={22} height={i === 0 || i === 5 ? 28 : 34} rx={7} fill={u('chromeV')} stroke="#1A0C26" strokeWidth={2} />
            <rect x={x - 11} y={736} width={22} height={34} rx={7} fill={u('sweep')} style={{ mixBlendMode: 'screen' }} />
            <rect x={x - 6} y={740} width={5} height={12} rx={2.5} fill="#fff" opacity={0.85} />
          </g>
        ))}
      </g>
      <path
        d="M 398 744 C 430 712 470 708 500 724 C 530 708 570 712 602 744 C 560 748 530 750 500 747 C 470 750 440 748 398 744 Z"
        fill={u('lipsTop')}
        stroke="#5A0848"
        strokeWidth={2}
      />
      <path
        d="M 404 756 C 440 768 470 772 500 772 C 530 772 560 768 596 756 C 582 810 542 826 500 826 C 458 826 418 810 404 756 Z"
        fill={u('lips')}
        stroke="#5A0848"
        strokeWidth={2}
      />
      <ellipse cx={470} cy={790} rx={36} ry={12} fill="#fff" opacity={0.85} transform="rotate(-6 470 790)" />
      <ellipse cx={530} cy={796} rx={12} ry={5} fill="#fff" opacity={0.7} />
      <ellipse cx={455} cy={724} rx={20} ry={6} fill="#fff" opacity={0.55} transform="rotate(-18 455 724)" />
      </g>

      {/* Gotas de agua sobre la piel; brillan cuando pasa el barrido. */}
      {[
        [596, 330, 16],
        [372, 300, 12],
        [712, 700, 14],
        [575, 612, 10],
        [258, 430, 11],
      ].map(([x, y, r], i) => (
        <Droplet key={i} cx={x} cy={y} r={r} glint={Math.max(0, 1 - Math.abs(x + y * 0.6 - sx - 120) / 140)} />
      ))}

      {/* Lágrima por la mejilla izquierda. */}
      {tear ? (
        <g opacity={tear.o}>
          <path d={`M ${tear.x + 4} 588 C ${tear.x + 2} ${tear.y - 40} ${tear.x} ${tear.y - 20} ${tear.x} ${tear.y}`} stroke="#fff" strokeOpacity={0.35} strokeWidth={5} fill="none" strokeLinecap="round" />
          <Droplet cx={tear.x} cy={tear.y} r={10} />
        </g>
      ) : null}

      {/* Gota que se forma en el labio y cae. */}
      {lipDrop ? (
        <g opacity={lipDrop.o} transform={`translate(504 ${lipDrop.y}) scale(1 ${lipDrop.stretch})`}>
          <path
            d={`M 0 ${-lipDrop.r * 1.6} C ${lipDrop.r * 0.4} ${-lipDrop.r * 0.6} ${lipDrop.r} ${-lipDrop.r * 0.2} ${lipDrop.r} ${lipDrop.r * 0.3} A ${lipDrop.r} ${lipDrop.r} 0 1 1 ${-lipDrop.r} ${lipDrop.r * 0.3} C ${-lipDrop.r} ${-lipDrop.r * 0.2} ${-lipDrop.r * 0.4} ${-lipDrop.r * 0.6} 0 ${-lipDrop.r * 1.6} Z`}
            fill={u('lips')}
            stroke="#5A0848"
            strokeWidth={1.5}
          />
          <ellipse cx={-lipDrop.r * 0.35} cy={0} rx={lipDrop.r * 0.25} ry={lipDrop.r * 0.35} fill="#fff" opacity={0.85} />
        </g>
      ) : null}

      {/* Respiración de color muy lenta en el rubor (sin mover la cabeza). */}
      <g clipPath={u('head')} opacity={0.12 + 0.1 * pulse(t, 1, 0.25)}>
        <ellipse cx={500} cy={640} rx={260} ry={120} fill={u('blush')} />
      </g>
    </svg>
  );
};
