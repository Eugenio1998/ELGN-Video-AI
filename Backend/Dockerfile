# 🐍 Imagem base oficial do Python
FROM python:3.11-slim

# 🛠️ Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# 📁 Diretório de trabalho
WORKDIR /code

# 🧱 Dependências de sistema para build de pacotes Python (necessário para watchdog)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    ffmpeg \
    libgl1 \
    git \
    libsm6 \
    libxext6 \
    libxrender-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 📜 Instala dependências
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -r requirements-dev.txt

# 📂 Copia o restante dos arquivos
COPY . .

# 🔓 Permissões de execução
RUN chmod +x /code/entrypoint.sh /code/entrypoint-celery.sh

# ✅ Corrige problemas de importação
ENV PYTHONPATH=/code