#!/bin/bash

echo "🔧 Aplicando migrações e preparando ambiente..."
echo "⏳ Aguardando Redis..."
sleep 3

# Verifica se Redis está respondendo
until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  echo "⏳ Esperando Redis em $REDIS_HOST:$REDIS_PORT..."
  sleep 1
done

echo "✅ Redis disponível. Iniciando Celery..."

# Executa o worker com reinício automático em caso de mudanças no código
watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- \
    celery -A backend.app.celery_app worker --loglevel=info --concurrency=2
