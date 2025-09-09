#!/bin/bash

# Configuração
EMAIL="admin@elgn.ai"
PASSWORD="12345678"
BASE_URL="http://localhost:8000"

# Login inicial
echo "🔐 Iniciando login para $EMAIL..."
curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}"
echo -e "\n🚨 Pegue o código 2FA via Redis (DB=2):"
echo "redis-cli -h redis -n 2 keys *"
