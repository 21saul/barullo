import type { ReactNode } from "react";

/**
 * Sello redondo de adorno, de los de pegatina: un texto que da la vuelta al
 * borde y algo en el centro. Tres formas: `scallop` (borde dentado de sello de
 * lacre), `disc` (círculo lleno) y `ring` (sólo contorno). Siempre decorativo.
 */
const SCALLOP = (() => {
  const teeth = 28;
  const pts: string[] = [];
  for (let i = 0; i < teeth * 2; i++) {
    const r = i % 2 ? 92 : 99;
    const a = (Math.PI * i) / teeth;
    pts.push(`${(100 + r * Math.sin(a)).toFixed(1)} ${(100 - r * Math.cos(a)).toFixed(1)}`);
  }
  return `M${pts.join("L")}Z`;
})();

export function Stamp({
  id,
  text,
  shape,
  bg,
  fg,
  children,
  className,
}: {
  /** Único en la página: lo usa el trazado del texto circular. */
  id: string;
  /** Texto del borde; se estira para dar la vuelta entera. */
  text: string;
  shape: "scallop" | "disc" | "ring";
  bg: string;
  fg: string;
  children?: ReactNode;
  className?: string;
}) {
  const path = `stamp-${id}`;
  return (
    <div aria-hidden="true" className={`relative ${className ?? ""}`} style={{ color: fg }}>
      <svg viewBox="0 0 200 200" className="block size-full">
        {shape === "scallop" && <path d={SCALLOP} fill={bg} />}
        {shape === "disc" && <circle cx="100" cy="100" r="98" fill={bg} />}
        {shape === "ring" && <circle cx="100" cy="100" r="96" fill={bg} stroke={fg} strokeWidth="3" />}
        <circle cx="100" cy="100" r="58" fill="none" stroke={fg} strokeWidth="2.5" strokeDasharray={shape === "ring" ? "5 6" : undefined} />
        <path id={path} d="M100 28a72 72 0 1 1 0 144a72 72 0 1 1 0-144" fill="none" />
        <text className="wide" fontSize="21" fill={fg}>
          <textPath href={`#${path}`} textLength="446" lengthAdjust="spacing">
            {text}
          </textPath>
        </text>
      </svg>
      <div className="absolute inset-[32%] flex items-center justify-center">{children}</div>
    </div>
  );
}
