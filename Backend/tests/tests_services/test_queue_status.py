"""
Teste de importação e estrutura para o serviço: queue_status
"""

def test_import_queue_status():
    try:
        import app.services.queue_status as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar queue_status: {e}"
