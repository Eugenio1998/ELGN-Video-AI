# 📦 Tarefa Celery para analytics (placeholder)

from celery import shared_task
import logging

logger = logging.getLogger("analytics_queue")

@shared_task(name="analytics.dummy_task")
def dummy_analytics_task():
    """
    🔧 Tarefa fictícia de analytics.
    Pode ser substituída futuramente por lógica de análise real (ex: tracking, relatórios).
    """
    logger.info("📈 Tarefa de analytics executada (dummy).")
    return "Tarefa de analytics executada (placeholder)"
