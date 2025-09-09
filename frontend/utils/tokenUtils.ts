// 📁 utils/tokenUtils.ts

export function isTokenExpired(token: string): boolean {
  try {
    const [, payloadBase64] = token.split(".");
    const decoded = JSON.parse(atob(payloadBase64));
    const now = Math.floor(Date.now() / 1000); // tempo atual em segundos

    return decoded.exp && now > decoded.exp;
  } catch (err) {
    console.error("❌ Erro ao verificar expiração do token:", err);
    return true; // se der erro, assume que está expirado
  }
}
