import jwt, { JwtPayload } from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  throw new Error("❌ JWT_SECRET não definido no ambiente.");
}

const SECRET_KEY: string = JWT_SECRET;

// ✅ Interface do payload esperado
export interface DecodedToken extends JwtPayload {
  id: string;
  email?: string;
  name?: string;
  picture?: string;
}

export function verifyToken(token: string): DecodedToken | null {
  try {
    const decoded = jwt.verify(token, SECRET_KEY) as DecodedToken;
    return decoded;
  } catch (error: unknown) {
    console.warn("❌ Erro ao verificar token:", error);
    return null;
  }
}

export function signToken(payload: DecodedToken): string {
  return jwt.sign(payload, SECRET_KEY, { expiresIn: "7d" });
}
