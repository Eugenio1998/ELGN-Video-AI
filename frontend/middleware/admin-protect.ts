// 📁 middleware/admin-protect.ts

import { GetServerSidePropsContext } from "next";
import { parseCookies } from "nookies";
import jwt from "jsonwebtoken";

interface DecodedToken {
  sub: string;
  email: string;
  role: "user" | "admin" | "manager";
  exp: number;
}

export async function requireAdmin(ctx: GetServerSidePropsContext) {
  // 🔓 Se autenticação estiver desativada, libera acesso geral
  if (process.env.DISABLE_AUTH === "true") {
    return { props: {} };
  }

  const { token } = parseCookies(ctx);

  if (!token) {
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as DecodedToken;

    if (decoded.role !== "admin") {
      return {
        redirect: {
          destination: "/unauthorized",
          permanent: false,
        },
      };
    }

    return { props: {} };
  } catch (err) {
    console.warn("Erro ao verificar token de admin:", err);
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }
}
