// 📁 pages/api/rate-limit.ts
import LRU from "lru-cache";
import type { NextApiResponse } from "next";

type Options = {
  uniqueTokenPerInterval?: number; // Quantidade máxima de IPs únicos
  interval?: number; // Janela de tempo em milissegundos
  max?: number; // Não utilizado (reservado para futuras melhorias)
};

/**
 * 🚫 Middleware de proteção por limite de requisições (Rate Limit).
 * Utiliza cache LRU para limitar o número de requisições por token/IP.
 */
const rateLimit = (options?: Options) => {
  const tokenCache = new LRU<string, number>({
    max: options?.uniqueTokenPerInterval ?? 500,
    ttl: options?.interval ?? 60 * 1000, // Padrão: 1 minuto
  });

  return {
    /**
     * Verifica se o token ultrapassou o limite. Rejeita a requisição se excedido.
     */
    check: (
      res: NextApiResponse,
      limit: number,
      token: string
    ): Promise<void> =>
      new Promise((resolve, reject) => {
        // ⚙️ Ignora rate-limit no ambiente de desenvolvimento
        if (process.env.NODE_ENV === "development") {
          return resolve();
        }

        const current = tokenCache.get(token) ?? 0;

        if (current >= limit) {
          console.warn(`🚨 Rate limit excedido para token/IP: ${token}`);
          res.status(429).json({
            error: "Muitas tentativas. Aguarde e tente novamente.",
          });
          return reject(new Error("Rate limit exceeded"));
        }

        tokenCache.set(token, current + 1);
        resolve();
      }),
  };
};

export default rateLimit;
