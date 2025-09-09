// 📁 middleware/user-protect.ts

import { GetServerSidePropsContext } from "next";
import { parseCookies } from "nookies";
import jwt from "jsonwebtoken";

interface DecodedToken {
  sub: string;
  email: string;
  role: "user" | "admin" | "manager";
  exp: number;
}

export async function requireUser(ctx: GetServerSidePropsContext) {
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

    if (
      decoded.role !== "user" &&
      decoded.role !== "manager" &&
      decoded.role !== "admin"
    ) {
      return {
        redirect: {
          destination: "/unauthorized",
          permanent: false,
        },
      };
    }

    return { props: {} };
  } catch (err) {
    console.warn("Erro ao verificar token do usuário:", err);
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }
}
