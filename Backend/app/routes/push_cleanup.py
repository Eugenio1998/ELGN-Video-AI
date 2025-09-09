import os
import json
import redis
import logging
from typing import Dict, List, Union
from pywebpush import webpush, WebPushException

# === 🔐 Configurações do VAPID ===
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
if not VAPID_PRIVATE_KEY:
    raise RuntimeError("❌ VAPID_PRIVATE_KEY não configurada nas variáveis de ambiente.")

# === 🧠 Conexão com Redis ===
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

# === 📋 Logger local ===
logger = logging.getLogger("push_cleanup")
logger.setLevel(logging.INFO)


def validate_and_clean_push_subscriptions(rdb=redis_client) -> Dict[str, Union[int, List[str]]]:
    """
    🔍 Valida todas as inscrições push armazenadas no Redis.
    ❌ Remove inscrições inválidas, expiradas ou malformadas.

    Retorna:
        - removed (List[str]): Lista de chaves removidas
        - total_checked (int): Total de inscrições verificadas
    """
    keys = rdb.keys("push_sub:*")
    removed_keys = []

    for key in keys:
        try:
            sub_data = rdb.get(key)
            if not sub_data:
                logger.warning(f"📭 Dados vazios — removendo chave: {key}")
                rdb.delete(key)
                removed_keys.append(key)
                continue

            subscription_info = json.loads(sub_data)

            # Envia um ping silencioso (teste de validade)
            webpush(
                subscription_info=subscription_info,
                data=json.dumps({"type": "ping"}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:admin@elgn.ai"},
            )

        except WebPushException as e:
            logger.warning(f"📤 Inscrição inválida removida: {key} — Motivo: {e}")
            rdb.delete(key)
            removed_keys.append(key)

        except json.JSONDecodeError:
            logger.warning(f"📤 Inscrição malformada (JSON) removida: {key}")
            rdb.delete(key)
            removed_keys.append(key)

        except Exception as e:
            logger.exception(f"⚠️ Erro inesperado ao validar inscrição {key}: {e}")

    return {
        "removed": removed_keys,
        "total_checked": len(keys)
    }
