# 🧼 Serviço de Limpeza de Arquivos Temporários

import os
import time
import logging

# === 🛠️ Logger ===
logger = logging.getLogger("file_cleaner")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 📁 Configurações ===
TMP_DIR = "/tmp"
MAX_AGE_SECONDS = 6 * 3600  # 6 horas

# === 🔐 Segurança ===
def is_path_safe(path: str, base_dir: str) -> bool:
    """Verifica se o caminho está dentro do diretório base, evitando path traversal."""
    return os.path.realpath(path).startswith(os.path.realpath(base_dir))

# === 🧽 Limpeza de Arquivos Temporários ===
def clean_temp_files(directory: str = TMP_DIR, max_age_seconds: int = MAX_AGE_SECONDS) -> int:
    """
    Remove arquivos e diretórios vazios mais antigos que `max_age_seconds` no diretório especificado.
    
    Retorna:
        int: Quantidade total de arquivos ou diretórios removidos.
    """
    now = time.time()
    removed_count = 0

    if not os.path.exists(directory):
        logger.warning(f"⚠️ Diretório não encontrado: {directory}. Nenhuma limpeza realizada.")
        return 0

    for item in os.listdir(directory):
        path = os.path.join(directory, item)

        if not is_path_safe(path, directory):
            logger.warning(f"🚫 Caminho inseguro ignorado: {path}")
            continue

        try:
            age = now - os.path.getmtime(path)

            if os.path.isfile(path) and age > max_age_seconds:
                os.remove(path)
                removed_count += 1
                logger.info(f"🗑️ Arquivo removido: {path}")

            elif os.path.isdir(path) and age > max_age_seconds:
                if not os.listdir(path):  # diretório vazio
                    os.rmdir(path)
                    removed_count += 1
                    logger.info(f"🗑️ Diretório removido: {path}")
                else:
                    logger.debug(f"📁 Diretório não vazio ignorado: {path}")

        except PermissionError:
            logger.warning(f"🔒 Sem permissão para remover: {path}")
        except OSError as e:
            logger.error(f"❌ Erro ao remover '{path}': {e}")
        except Exception as e:
            logger.error(f"⚠️ Erro inesperado ao processar '{path}': {e}")

    logger.info(f"✅ Limpeza finalizada. Total removido: {removed_count}")
    return removed_count

# === 🔧 Execução manual ===
if __name__ == "__main__":
    logger.info("🧽 Iniciando limpeza manual de arquivos temporários...")
    total = clean_temp_files()
    logger.info(f"🧹 Total de itens removidos: {total}")
