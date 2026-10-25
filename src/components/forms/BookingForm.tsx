"use client";

import { useActionState } from "react";
import { requestBooking, type FormState } from "@/app/actions";
import { Field, TextArea, Select } from "@/components/ui/Field";
import { Button } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { SelloMedalla } from "@/components/brand/SelloMedalla";

/**
 * Formulario de propuestas (noches, showcases, uso fuera de horario): cambian los
 * tipos del desplegable, no la lógica.
 */
export function BookingForm({
  tipos,
  submitLabel = "Enviar solicitud",
}: {
  tipos: string[];
  submitLabel?: string;
}) {
  const [state, action, pending] = useActionState<FormState | null, FormData>(requestBooking, null);

  if (state?.ok) {
    return (
      <div className="panel flex flex-col items-center gap-6 p-8 text-center sm:flex-row sm:text-left" role="status">
        <SelloMedalla id="propuesta" text="PROPUESTA RECIBIDA · BARULLO · " stamped className="size-36 shrink-0" />
        <div>
          <p className="caps flex items-center justify-center gap-2 text-lg text-milk sm:justify-start">
            <Icon name="CircleCheck" className="shrink-0 text-acid" />
            Solicitud recibida
          </p>
          <p className="mt-1 text-sm text-ash">{state.message}</p>
        </div>
      </div>
    );
  }

  return (
    <form action={action} className="flex flex-col gap-5" noValidate>
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Nombre y apellidos" name="nombre" required autoComplete="name" error={state?.errors?.nombre} />
        <Field label="Teléfono" name="telefono" type="tel" inputMode="tel" required autoComplete="tel" error={state?.errors?.telefono} />
      </div>
      <Field label="Correo" name="email" type="email" inputMode="email" spellCheck={false} autoCapitalize="off" required autoComplete="email" error={state?.errors?.email} />
      <div className="grid gap-5 sm:grid-cols-3">
        <Select label="Tipo" name="tipo" required defaultValue={tipos[0]} error={state?.errors?.tipo}>
          {tipos.map((t) => (
            <option key={t} value={t} className="bg-coal">
              {t}
            </option>
          ))}
        </Select>
        <Field label="Fecha" name="fecha" type="date" required error={state?.errors?.fecha} />
        <Field label="Personas" name="personas" type="number" min={1} max={500} defaultValue={8} required error={state?.errors?.personas} />
      </div>
      <TextArea
        label="Cuéntanos más"
        name="mensaje"
        hint="Motivo, horario aproximado, si necesitáis algo especial…"
        error={state?.errors?.mensaje}
      />
      {state && !state.ok && (
        <p role="alert" className="text-sm font-medium text-blood">
          {state.message}
        </p>
      )}
      <Button type="submit" disabled={pending} className="self-start">
        {pending ? "Enviando…" : submitLabel}
      </Button>
    </form>
  );
}
