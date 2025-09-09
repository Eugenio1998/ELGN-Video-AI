"""
Teste de importação e estrutura para o serviço: celery_monitoring
"""

def test_import_celery_monitoring():
    try:
        import app.services.celery_monitoring as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar celery_monitoring: {e}"
