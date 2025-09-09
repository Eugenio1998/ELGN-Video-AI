// 📁 utils/verifyToken.ts
import jwt, { JwtPayload } from "jsonwebtoken";

export interface DecodedUser extends JwtPayload {
  id: string;
  email?: string;
  plan?: string;
  username?: string;
}

export function verifyToken(token: string): DecodedUser | null {
  const secret = process.env.JWT_SECRET_KEY;

  if (!secret) {
    console.error("❌ JWT_SECRET_KEY não está definido.");
    return null;
  }

  try {
    const decoded = jwt.verify(token, secret) as JwtPayload;

    const id = typeof decoded === "object" ? (decoded.id ?? decoded.sub) : null;

    if (!id || typeof id !== "string") {
      throw new Error("Token decodificado não possui ID ou sub válido.");
    }

    return {
      id,
      email: decoded.email,
      plan: decoded.plan,
      username: decoded.username,
      exp: decoded.exp,
      iat: decoded.iat,
    };
  } catch (err) {
    console.error("❌ Token inválido:", err);
    return null;
  }
}
