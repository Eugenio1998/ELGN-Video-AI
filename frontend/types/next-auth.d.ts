// 📁 types/next-auth.d.ts
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import type { Session } from "next-auth"; // força o carregamento dos tipos base
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import type { JWT } from "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
      plan?: string;
    };
  }

  interface User {
    id: string;
    plan?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    email?: string | null;
    name?: string | null;
    picture?: string | null;
    plan?: string;
  }
}
