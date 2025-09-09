import { buffer } from "micro";
import type { NextApiRequest, NextApiResponse } from "next";
import Stripe from "stripe";
import axios from "axios";
import { sendWelcomeEmail } from "../webhook/emailSender";

export const config = {
  api: {
    bodyParser: false,
  },
};

const stripeSecret = process.env.STRIPE_SECRET_KEY;
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
const backendURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

if (!stripeSecret || !webhookSecret) {
  throw new Error(
    "❌ STRIPE_SECRET_KEY ou STRIPE_WEBHOOK_SECRET não definidos."
  );
}

const stripe = new Stripe(stripeSecret, {
  apiVersion: "2022-11-15",
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).end("Method Not Allowed");
  }

  const buf = await buffer(req);
  const sig = req.headers["stripe-signature"];

  if (!sig) {
    return res.status(400).send("❌ Assinatura ausente no cabeçalho.");
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(buf, sig, webhookSecret!);
  } catch (err) {
    console.error("❌ Webhook inválido:", err);
    return res.status(400).send(`Webhook Error: ${(err as Error).message}`);
  }

  const tipo = event.type;
  const id = event.id;

  // ✅ Envia evento para o backend salvar no banco
  try {
    await axios.post(`${backendURL}/api/v1/webhook/stripe`, {
      id,
      type: tipo,
    });
  } catch {
    console.warn("⚠️ Falha ao registrar evento no backend:", id);
  }

  // ✅ Evento: Pagamento concluído
  if (tipo === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;
    const email = session.customer_email;
    const plano = session?.metadata?.plano || "desconhecido";

    if (email) {
      await sendWelcomeEmail(email, "Gerlyane", plano);
      console.info("✅ Pagamento confirmado:", { email, plano });
    }

    return res.status(200).json({ received: true });
  }

  // ⚠️ Evento: Pagamento falhou
  if (tipo === "invoice.payment_failed") {
    const invoice = event.data.object as Stripe.Invoice;
    const customer = await stripe.customers.retrieve(
      invoice.customer as string
    );
    const email = (customer as Stripe.Customer).email;

    console.warn("💸 Pagamento falhou para:", email || "Email não encontrado");
    return res.status(200).end("Falha de pagamento tratada");
  }

  // ⚠️ Evento: Assinatura cancelada
  if (tipo === "customer.subscription.deleted") {
    const subscription = event.data.object as Stripe.Subscription;

    try {
      const customer = await stripe.customers.retrieve(
        subscription.customer as string
      );
      const email = (customer as Stripe.Customer).email;
      console.info("🔁 Assinatura cancelada:", email || "Email não encontrado");
    } catch {
      console.warn("❌ Não foi possível obter o e-mail do cliente.");
    }

    return res.status(200).end("Assinatura cancelada tratada");
  }

  // 📭 Evento ignorado
  console.warn("📭 Evento não tratado:", tipo);
  return res.status(200).end("Evento ignorado");
}
