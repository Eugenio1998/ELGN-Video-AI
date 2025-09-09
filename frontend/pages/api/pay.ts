// 📁 pages/api/pay.ts

import type { NextApiRequest, NextApiResponse } from "next";
import Stripe from "stripe";

if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error("❌ STRIPE_SECRET_KEY não está definida no ambiente.");
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: "2022-11-15",
});

const valoresUSD: Record<string, number> = {
  Basic: 10,
  Pro: 25,
  Premium: 50,
  Empresarial: 100,
  "Basic Anual": 100,
  "Pro Anual": 250,
  "Premium Anual": 500,
  "Empresarial Anual": 1000,
};

interface PayRequestBody {
  plano: keyof typeof valoresUSD;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método não permitido" });
  }

  const { plano } = req.body as PayRequestBody;

  if (!plano || !valoresUSD[plano]) {
    console.warn(`📛 Plano inválido recebido: ${plano}`);
    return res.status(400).json({ error: "Plano inválido" });
  }

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      line_items: [
        {
          price_data: {
            currency: "usd",
            product_data: { name: plano },
            unit_amount: valoresUSD[plano] * 100,
          },
          quantity: 1,
        },
      ],
      mode: "payment",
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/thanks`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/plans`,
      metadata: { plano },
    });

    console.info(`💳 Sessão Stripe criada para plano: ${plano}`);
    return res.status(200).json({ success: true, url: session.url });
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error("❌ Erro ao criar sessão Stripe:", error.message);
      return res.status(500).json({ error: "Erro ao processar pagamento" });
    }
    console.error("❌ Erro desconhecido ao criar sessão Stripe:", error);
    return res
      .status(500)
      .json({ error: "Erro desconhecido ao processar pagamento" });
  }
}
