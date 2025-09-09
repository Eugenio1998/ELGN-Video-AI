#!/bin/bash

echo "🔧 Aplicando migrações e preparando ambiente..."

echo "⏳ Aguardando Redis em $REDIS_HOST:$REDIS_PORT..."
# Aguarda o Redis estar disponível antes de iniciar a aplicação
until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  echo "⌛ Redis ainda não disponível, aguardando..."
  sleep 1
done
echo "✅ Redis disponível!"

echo "🚀 Iniciando FastAPI com Uvicorn..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
