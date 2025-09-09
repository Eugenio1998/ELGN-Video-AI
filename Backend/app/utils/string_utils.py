# 📁 app/utils/string_utils.py

import hashlib
import re
import unicodedata


# === 🔗 Slug seguro para URLs ===
def slugify(text: str, preserve_case: bool = False) -> str:
    """
    Converte um texto em um slug seguro para URLs.
    Exemplo: 'Título de Vídeo' → 'titulo-de-video'
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)  # Remove caracteres especiais
    text = text.strip()
    text = text if preserve_case else text.lower()
    return re.sub(
        r"[-\s]+", "-", text
    )  # Substitui espaços e traços múltiplos por '-'


# === 🧼 Nome de arquivo seguro ===
def sanitize_filename(filename: str) -> str:
    """
    Remove caracteres inválidos para nomes de arquivos.
    Exemplo: 'vídeo*?.mp4' → 'vídeo___.mp4'
    """
    return re.sub(r"[^\w\-_.]", "_", filename)


# === ✂️ Reduz texto com limite ===
def shorten_text(text: str, max_length: int = 100) -> str:
    """
    Corta o texto com reticências se ultrapassar o limite.
    Exemplo: 'Texto muito longo aqui' → 'Texto muito lo...'
    """
    return text if len(text) <= max_length else text[: max_length - 3] + "..."


# === 🔐 Hash SHA256 ===
def hash_string_sha256(text: str) -> str:
    """
    Gera hash SHA256 de uma string.
    """
    return hashlib.sha256(text.encode()).hexdigest()


# === 🧾 Hash MD5 (uso leve) ===
def hash_string_md5(text: str) -> str:
    """
    Gera hash MD5 de uma string (menos seguro, mas útil para checksum simples).
    """
    return hashlib.md5(text.encode()).hexdigest()


# === 🔤 Remove acentos ===
def remove_accents(text: str) -> str:
    """
    Remove acentuação da string.
    Exemplo: 'Edição de vídeo' → 'Edicao de video'
    """
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ASCII", "ignore")
        .decode("utf-8")
    )


# === 🧽 Limpa HTML ===
def remove_html_tags(text: str) -> str:
    """
    Remove tags HTML de um texto.
    Exemplo: '<b>Olá</b>' → 'Olá'
    """
    return re.sub(r"<[^>]*?>", "", text)


# === 📦 Exportação explícita ===
__all__ = [
    "slugify",
    "sanitize_filename",
    "shorten_text",
    "hash_string_sha256",
    "hash_string_md5",
    "remove_accents",
    "remove_html_tags",
]
