"use server";

import { z } from "zod";

/**
 * Server Actions de los formularios. Hoy sólo validan y registran: no hay
 * integración real con proveedor de email ni CRM.
 *
 * TODO antes de producción: conectar `subscribe` a Mailchimp/Brevo/Resend y
 * `sendContact`/`requestBooking` a la bandeja del club. Mientras tanto NO se
 * guarda nada: los envíos se pierden.
 */

const emailSchema = z.object({
  email: z.email({ message: "Revisa el correo: no parece válido." }),
});

const contactSchema = z.object({
  nombre: z.string().min(2, "Dinos cómo te llamas."),
  email: z.email("Revisa el correo: no parece válido."),
  asunto: z.string().min(1),
  mensaje: z.string().min(10, "Cuéntanos un poco más (mínimo 10 caracteres)."),
});

const bookingSchema = z.object({
  nombre: z.string().min(2, "Dinos cómo te llamas."),
  email: z.email("Revisa el correo: no parece válido."),
  telefono: z.string().min(9, "Necesitamos un teléfono de contacto."),
  fecha: z.string().min(1, "Elige una fecha."),
  personas: z.coerce.number().int().min(1).max(500),
  tipo: z.string().min(1),
  mensaje: z.string().optional(),
});

export type FormState = {
  ok: boolean;
  message: string;
  errors?: Record<string, string[]>;
};

function fail(parsed: z.ZodError): FormState {
  return {
    ok: false,
    message: "Falta algún dato. Revisa lo marcado y vuelve a enviar.",
    errors: z.flattenError(parsed).fieldErrors as Record<string, string[]>,
  };
}

export async function subscribe(formData: FormData): Promise<void> {
  const parsed = emailSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return;
  console.info("[newsletter] alta pendiente de integrar:", parsed.data.email);
}

export async function sendContact(
  _prev: FormState | null,
  formData: FormData,
): Promise<FormState> {
  const parsed = contactSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return fail(parsed.error);
  console.info("[contacto] mensaje pendiente de integrar:", parsed.data);
  return { ok: true, message: "Mensaje enviado. Te respondemos en 24-48 h." };
}

export async function requestBooking(
  _prev: FormState | null,
  formData: FormData,
): Promise<FormState> {
  const parsed = bookingSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return fail(parsed.error);
  console.info("[reserva] solicitud pendiente de integrar:", parsed.data);
  return {
    ok: true,
    message: "Solicitud recibida. Te confirmamos disponibilidad por teléfono o correo.",
  };
}
