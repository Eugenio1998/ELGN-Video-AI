// 📁 pages/api/webhook/emailSender.ts
import nodemailer from "nodemailer";

/**
 * 📧 Envia e-mail de boas-vindas após confirmação de pagamento via Stripe.
 */
export async function sendWelcomeEmail(
  email: string,
  nome: string,
  plano: string
) {
  const user = process.env.EMAIL_USER;
  const pass = process.env.EMAIL_PASS;
  const site = process.env.NEXT_PUBLIC_SITE_URL;

  if (!user || !pass || !site) {
    throw new Error("❌ Variáveis de ambiente de e-mail não definidas.");
  }

  // 🔐 Transporter com configuração SMTP segura
  const transporter = nodemailer.createTransport({
    host: "smtp.gmail.com", // Pode ser outro provedor (ex: SendGrid, SES)
    port: 587,
    secure: false,
    auth: { user, pass },
  });

  // 🖼️ HTML do e-mail
  const html = `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="description" content="Sua assinatura foi confirmada! Bem-vinda ao ELGN Video.AI." />
      <title>Assinatura Confirmada</title>
    </head>
    <body style="background:#0d0d0d; color:#ffffff; font-family:sans-serif; padding:40px;">
      <div style="max-width:600px; margin:auto; border-radius:12px; border:1px solid #2ecc71; padding:32px; background:#0e0e0e;">
        <img src="${site}/img/ELGN-AI.png" alt="Logo ELGN" width="120" style="margin-bottom:24px;" />
        <h1 style="color:#2ecc71;">✅ Assinatura Confirmada!</h1>
        <p>Olá <strong>${nome}</strong>,</p>
        <p>Bem-vinda ao <strong>ELGN Video.AI</strong>! Sua assinatura do plano <strong>${plano}</strong> foi confirmada com sucesso.</p>
        <p>Agora você tem acesso ao nosso editor de vídeo com inteligência artificial, geração de conteúdo, vozes e filtros inteligentes.</p>
        <a href="${site}/dashboard"
           style="display:inline-block; margin-top:24px; padding:14px 28px; background:linear-gradient(to right,#2ecc71,#a6ff4d); color:#000; font-weight:bold; text-decoration:none; border-radius:8px;">
          ➡️ Acessar meu painel
        </a>
        <p style="margin-top:32px; font-size:14px; color:#aaaaaa;">
          Precisa de ajuda? <a href="mailto:support@elgn.ai" style="color:#2ecc71;">Fale conosco</a>
        </p>
        <p style="font-size:12px; color:#888; margin-top:40px;">© 2025 ELGN Video.AI</p>
      </div>
    </body>
    </html>
  `;

  // 📤 Envio do e-mail
  await transporter.sendMail({
    from: `"ELGN Video.AI" <${user}>`,
    to: email,
    subject: "✅ Pagamento Confirmado - Bem-vinda ao ELGN",
    html,
  });

  console.info(`📧 E-mail de boas-vindas enviado para ${email}`);
}
