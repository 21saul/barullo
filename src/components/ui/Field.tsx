import type { ComponentProps, ReactNode } from "react";
import { Icon } from "@/components/ui/Icon";
import { cn } from "@/lib/utils";

/* `focus:outline-none` estaba matando el anillo de foco global: un cambio de
   color de borde de 1 px no es un indicador de foco suficiente para quien
   navega con teclado. Se deja el anillo y el borde acompaña. */
const CONTROL =
  "min-h-13 w-full rounded-md border border-rule bg-slate px-4 text-base font-semibold text-milk placeholder:text-dust transition-colors duration-150 focus-visible:border-acid";

function Wrapper({
  label,
  htmlFor,
  error,
  hint,
  children,
  className,
}: {
  label: string;
  htmlFor: string;
  error?: string[];
  hint?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <label htmlFor={htmlFor} className="text-sm font-bold text-milk">
        {label}
      </label>
      {children}
      {hint && !error && <p className="text-xs text-dust">{hint}</p>}
      {error && (
        <p id={`${htmlFor}-error`} role="alert" className="text-xs font-medium text-blood">
          {error[0]}
        </p>
      )}
    </div>
  );
}

type Common = { label: string; error?: string[]; hint?: string; wrapperClassName?: string };

export function Field({
  label,
  error,
  hint,
  wrapperClassName,
  id,
  ...rest
}: Common & ComponentProps<"input">) {
  const fieldId = id ?? rest.name!;
  return (
    <Wrapper label={label} htmlFor={fieldId} error={error} hint={hint} className={wrapperClassName}>
      <input
        id={fieldId}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? `${fieldId}-error` : undefined}
        className={CONTROL}
        {...rest}
      />
    </Wrapper>
  );
}

export function TextArea({
  label,
  error,
  hint,
  wrapperClassName,
  id,
  ...rest
}: Common & ComponentProps<"textarea">) {
  const fieldId = id ?? rest.name!;
  return (
    <Wrapper label={label} htmlFor={fieldId} error={error} hint={hint} className={wrapperClassName}>
      <textarea
        id={fieldId}
        rows={5}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? `${fieldId}-error` : undefined}
        className={cn(CONTROL, "min-h-32 py-3")}
        {...rest}
      />
    </Wrapper>
  );
}

export function Select({
  label,
  error,
  hint,
  wrapperClassName,
  id,
  children,
  ...rest
}: Common & ComponentProps<"select">) {
  const fieldId = id ?? rest.name!;
  return (
    <Wrapper label={label} htmlFor={fieldId} error={error} hint={hint} className={wrapperClassName}>
      {/* `appearance-none` quita la flecha nativa, así que hay que poner una:
          sin ella el campo parece un input de texto que no se puede escribir.
          El color de fondo va explícito porque el desplegable nativo no hereda
          el tema oscuro en todos los navegadores. */}
      <div className="relative">
        <select
          id={fieldId}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${fieldId}-error` : undefined}
          className={cn(CONTROL, "appearance-none pr-11")}
          {...rest}
        >
          {children}
        </select>
        <Icon
          name="ChevronDown"
          size={16}
          className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-ash"
        />
      </div>
    </Wrapper>
  );
}
