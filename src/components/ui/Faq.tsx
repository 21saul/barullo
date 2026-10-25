/** Acordeón nativo con <details>: accesible y sin una línea de JavaScript. */
export function Faq({ items }: { items: readonly { q: string; a: string }[] }) {
  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.q}>
          <details className="group rounded-md bg-coal px-5 py-4 ring-1 ring-rule open:ring-edge">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-6 text-left text-[17px] font-black leading-snug text-milk transition-colors hover:text-acid [&::-webkit-details-marker]:hidden">
              {item.q}
              <span
                aria-hidden="true"
                className="shrink-0 text-2xl font-normal text-acid transition-transform duration-200 group-open:rotate-45"
              >
                +
              </span>
            </summary>
            <p className="mt-3 max-w-2xl leading-relaxed text-ash">{item.a}</p>
          </details>
        </li>
      ))}
    </ul>
  );
}
