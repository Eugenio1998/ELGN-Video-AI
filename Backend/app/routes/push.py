import os
import json
import logging
from typing import Dict, Any, Optional
from pywebpush import webpush, WebPushException
from dotenv import load_dotenv

load_dotenv()

# === 📋 Logger Local ===
logger = logging.getLogger("push_utils")
logger.setLevel(logging.INFO)

# === 🔐 Configurações VAPID
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "admin@elgn.ai")

if not VAPID_PUBLIC_KEY or not VAPID_PRIVATE_KEY:
    logger.critical("⚠️ VAPID keys não configuradas no .env")
    raise RuntimeError("❌ VAPID_PUBLIC_KEY e/ou VAPID_PRIVATE_KEY ausentes no ambiente.")


# === ✅ Validador de inscrição push
def validate_subscription_info(subscription: Dict[str, Any]) -> bool:
    return (
        isinstance(subscription, dict) and
        "endpoint" in subscription and
        isinstance(subscription.get("keys", {}).get("p256dh"), str) and
        isinstance(subscription.get("keys", {}).get("auth"), str)
    )


# === 🚀 Enviar notificação push para o navegador
def send_push_notification(subscription_info: Dict[str, Any], message: str) -> bool:
    if not validate_subscription_info(subscription_info):
        logger.warning("❌ Inscrição inválida para push notification.")
        return False

    try:
        webpush(
            subscription_info=subscription_info,
            data=message,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{VAPID_EMAIL}"},
        )
        logger.info("✅ Notificação push enviada com sucesso.")
        return True

    except WebPushException as e:
        logger.error(f"❌ Erro WebPush: {e}")
        if e.response and e.response.content:
            try:
                logger.error(f"↪️ Detalhes: {e.response.content.decode()}")
            except Exception:
                logger.warning("↪️ Erro ao decodificar conteúdo da resposta.")
        return False

    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar push: {e}")
        return False


# === 🧩 Formatar payload da notificação
def format_push_message(
    title: str,
    body: str,
    icon: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> str:
    try:
        payload = {
            "title": title,
            "body": body,
            "icon": icon or "/favicon.ico",
            "data": data or {},
        }
        return json.dumps(payload)

    except Exception as e:
        logger.error(f"❌ Erro ao formatar push message: {e}")
        return json.dumps({
            "title": "Erro",
            "body": "Não foi possível processar a mensagem push.",
        })
