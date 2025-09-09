// 📁 utils/auth.ts

export function getAuthData(): { token: string | null; userId: string | null } {
  const token = localStorage.getItem("token");
  const userId = localStorage.getItem("userId");
  return { token, userId };
}
