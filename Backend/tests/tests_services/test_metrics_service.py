"""
Teste de importação e estrutura para o serviço: metrics_service
"""

def test_import_metrics_service():
    try:
        import app.services.metrics_service as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar metrics_service: {e}"
