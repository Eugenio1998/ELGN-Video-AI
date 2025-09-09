"""
Teste de importação do módulo: celery_app
"""

def test_import_celery_app():
    try:
        import app.celery_app as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar celery_app: {e}"
