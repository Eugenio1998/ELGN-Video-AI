// 📂 components/Footer.tsx
import {
  FaFacebookF,
  FaInstagram,
  FaTiktok,
  FaYoutube,
  FaWhatsapp,
} from "react-icons/fa";
import { useTranslation } from "react-i18next";

export default function Footer() {
  const { t } = useTranslation();

  return (
    <>
      <footer
        role="contentinfo"
        className="bg-black text-white border-t border-white py-8 px-4 relative z-10"
      >
        <div className="max-w-screen-xl mx-auto grid gap-4 text-center sm:text-left sm:grid-cols-3">
          {/* Redes Sociais */}
          <div className="flex justify-center sm:justify-start space-x-4 text-xl">
            <a
              href="https://facebook.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Facebook"
              className="hover:text-cyan-400 transition"
            >
              <FaFacebookF />
            </a>
            <a
              href="https://instagram.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Instagram"
              className="hover:text-pink-400 transition"
            >
              <FaInstagram />
            </a>
            <a
              href="https://tiktok.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="TikTok"
              className="hover:text-white transition"
            >
              <FaTiktok />
            </a>
            <a
              href="https://youtube.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="YouTube"
              className="hover:text-red-500 transition"
            >
              <FaYoutube />
            </a>
            <a
              href="https://wa.me/5599999999999"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="WhatsApp"
              className="hover:text-green-400 transition"
            >
              <FaWhatsapp />
            </a>
          </div>

          {/* Contato */}
          <address className="text-sm not-italic">
            <p>
              📧{" "}
              <a href="mailto:elgn@tech.com" className="hover:text-cyan-300">
                elgn@tech.com
              </a>
            </p>
            <p>
              🌐{" "}
              <a href="https://elgn.tech" className="hover:text-cyan-300">
                elgn.tech
              </a>
            </p>
          </address>

          {/* Informações legais */}
          <section className="text-xs text-gray-400 sm:text-right">
            <p>© 2025 ELGN Video.AI</p>
            <p>{t("footer.rights")}</p>
          </section>
        </div>
      </footer>

      {/* 🔆 Linha neon pulsante multicolorida abaixo do footer */}
      <div className="h-[8px] w-full bg-gradient-to-r from-pink-500 via-yellow-300 to-cyan-400 animate-pulse blur-sm shadow-xl" />
    </>
  );
}
