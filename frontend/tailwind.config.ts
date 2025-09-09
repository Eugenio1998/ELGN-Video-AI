import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./app/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ["class", '[class*="theme-"]'], // 👈 Aqui o segredo
  theme: {
    extend: {
      colors: {
        sunset: "#f97316", // laranja por do sol
        cyan: "#22d3ee", // azul ciano
        blood: "#ef4444", // vermelho
        solar: "#facc15", // amarelo
        cyberpunk: "#0ff1ce",
        retro: "#f59e0b",
        futurista: "#9333ea",
      },
    },
  },
  plugins: [],
};

export default config;

// tailwind.config.js
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: ['bg-[url("/img/Mario02.gif")]'],
  theme: {
    extend: {},
  },
  plugins: [],
};
