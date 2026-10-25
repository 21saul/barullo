"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Pantalla de salidas de aeropuerto (split-flap) con las próximas noches.
 * Es el fondo del héroe de /agenda: se alimenta de la agenda real, así que
 * nunca se queda desfasado como lo haría un vídeo.
 *
 * Cada casilla pasa por unas cuantas letras al azar antes de caer en la suya,
 * y cada pocos segundos la pantalla «se actualiza»: sube una fila y entra la
 * siguiente noche, como en una estación. Con prefers-reduced-motion se pinta
 * quieta, ya con el texto final.
 *
 * Es decorativa (aria-hidden en PageHero): la misma información está en la
 * lista de la página, que es la que leen Google y los lectores de pantalla.
 */

export interface BoardRow {
  day: string; // "VIE 23"
  time: string; // "23:59"
  title: string;
  status: string; // "ÚLTIMAS", "A LA VENTA"...
  hot?: boolean; // en rojo (últimas entradas, agotado)
}

const SPIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

/** Una casilla: las dos mitades estáticas y dos hojas que caen al cambiar. */
function Flap({ target, delay, still }: { target: string; delay: number; still: boolean }) {
  const [cur, setCur] = useState(target);
  const [prev, setPrev] = useState(" ");
  const [n, setN] = useState(0);
  const curRef = useRef(cur);

  useEffect(() => {
    // Quieta se pinta `target` tal cual (ver abajo); sólo se apunta de dónde
    // tiene que arrancar el giro cuando se encienda.
    if (still) {
      curRef.current = target;
      return;
    }
    if (curRef.current === target) return;
    // Espacio a espacio no se anima: así las filas cortas no «tiemblan».
    const steps = target === " " ? 1 : 2 + Math.floor(Math.random() * 6);
    const timers: number[] = [];
    for (let i = 0; i < steps; i++) {
      timers.push(
        window.setTimeout(() => {
          const next = i === steps - 1 ? target : SPIN[Math.floor(Math.random() * SPIN.length)];
          setPrev(curRef.current);
          curRef.current = next;
          setCur(next);
          setN((k) => k + 1);
        }, delay + i * 85),
      );
    }
    return () => timers.forEach(clearTimeout);
  }, [target, delay, still]);

  if (still) {
    return (
      <span className="flap">
        <span className="flap-half flap-top">{target}</span>
        <span className="flap-half flap-bottom">{target}</span>
      </span>
    );
  }

  return (
    <span className="flap">
      <span className="flap-half flap-top">{cur}</span>
      <span className="flap-half flap-bottom">{prev}</span>
      {n > 0 && (
        <>
          <span key={`t${n}`} className="flap-half flap-top flap-leaf-top">
            {prev}
          </span>
          <span key={`b${n}`} className="flap-half flap-bottom flap-leaf-bottom">
            {cur}
          </span>
        </>
      )}
    </span>
  );
}

function Cells({
  text,
  width,
  delay,
  still,
  className,
}: {
  text: string;
  width: number;
  delay: number;
  still: boolean;
  className?: string;
}) {
  const chars = text.toUpperCase().slice(0, width).padEnd(width, " ").split("");
  return (
    <span className={cn("flex gap-[var(--flap-gap)]", className)}>
      {chars.map((c, i) => (
        <Flap key={i} target={c} delay={delay + i * 28} still={still} />
      ))}
    </span>
  );
}

export function DepartureBoard({ rows, visible = 6 }: { rows: BoardRow[]; visible?: number }) {
  const [offset, setOffset] = useState(0);
  // ssr: el texto final, quieto (es lo que ve quien pide menos movimiento).
  // blank → live: la pantalla se «enciende» en blanco y cada casilla gira
  // hasta su letra.
  const [phase, setPhase] = useState<"ssr" | "blank" | "live">("ssr");

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const blank = window.setTimeout(() => setPhase("blank"), 0);
    const boot = window.setTimeout(() => setPhase("live"), 400);
    const id =
      rows.length > 1 ? window.setInterval(() => setOffset((o) => (o + 1) % rows.length), 6500) : undefined;
    return () => {
      window.clearTimeout(blank);
      window.clearTimeout(boot);
      window.clearInterval(id);
    };
  }, [rows.length]);

  const still = phase === "ssr";
  const shown = Array.from({ length: Math.min(visible, Math.max(rows.length, 1)) }, (_, i) =>
    phase === "blank" || !rows.length ? undefined : rows[(offset + i) % rows.length],
  );

  return (
    <div className="board">
      <div className="board-head">
        <span>Próximas noches</span>
        <span className="hidden sm:inline">Salida · Noche · Estado</span>
      </div>
      <ul className="board-rows">
        {shown.map((r, i) => {
          const d = i * 140;
          return (
            <li key={i} className="board-row">
              <Cells text={r?.day ?? ""} width={6} delay={d} still={still} />
              <Cells text={r?.time ?? ""} width={5} delay={d + 60} still={still} className="hidden sm:flex" />
              <Cells text={r?.title ?? ""} width={16} delay={d + 120} still={still} className="board-title" />
              <Cells
                text={r?.status ?? ""}
                width={10}
                delay={d + 200}
                still={still}
                className={cn("hidden lg:flex", r?.hot ? "text-acid" : "text-milk/70")}
              />
            </li>
          );
        })}
      </ul>
    </div>
  );
}
