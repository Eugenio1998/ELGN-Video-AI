"""
Teste de importação e estrutura para o serviço: async_task_worker
"""

def test_import_async_task_worker():
    try:
        import app.services.async_task_worker as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar async_task_worker: {e}"
