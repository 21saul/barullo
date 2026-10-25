"use client";

import { useActionState } from "react";
import { sendContact, type FormState } from "@/app/actions";
import { Field, TextArea, Select } from "@/components/ui/Field";
import { Button } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { SelloMedalla } from "@/components/brand/SelloMedalla";

const ASUNTOS = [
  "Información general",
  "Entradas",
  "Booking / propuesta artística",
  "Prensa y colaboraciones",
  "Objetos perdidos",
  "Trabajar con nosotros",
];

export function ContactForm() {
  const [state, action, pending] = useActionState<FormState | null, FormData>(sendContact, null);

  if (state?.ok) {
    return (
      <div className="panel flex flex-col items-center gap-6 p-8 text-center sm:flex-row sm:text-left" role="status">
        <SelloMedalla id="enviado" text="MENSAJE RECIBIDO · BARULLO · " stamped className="size-36 shrink-0" />
        <div>
          <p className="caps flex items-center justify-center gap-2 text-lg text-milk sm:justify-start">
            <Icon name="CircleCheck" className="shrink-0 text-acid" />
            Mensaje enviado
          </p>
          <p className="mt-1 text-sm text-ash">{state.message}</p>
        </div>
      </div>
    );
  }

  return (
    <form action={action} className="flex flex-col gap-5" noValidate>
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Nombre" name="nombre" required autoComplete="name" error={state?.errors?.nombre} />
        <Field label="Correo" name="email" type="email" inputMode="email" spellCheck={false} autoCapitalize="off" required autoComplete="email" error={state?.errors?.email} />
      </div>
      <Select label="Asunto" name="asunto" required defaultValue={ASUNTOS[0]} error={state?.errors?.asunto}>
        {ASUNTOS.map((a) => (
          <option key={a} value={a} className="bg-coal">
            {a}
          </option>
        ))}
      </Select>
      <TextArea
        label="Mensaje"
        name="mensaje"
        required
        error={state?.errors?.mensaje}
        hint="Cuanto más concreto, antes te respondemos."
      />
      {state && !state.ok && (
        <p role="alert" className="text-sm font-medium text-blood">
          {state.message}
        </p>
      )}
      <Button type="submit" disabled={pending} className="self-start">
        {pending ? "Enviando…" : "Enviar mensaje"}
      </Button>
    </form>
  );
}
