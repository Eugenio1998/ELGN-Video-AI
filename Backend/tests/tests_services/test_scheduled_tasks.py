"""
Teste de importação e estrutura para o serviço: scheduled_tasks
"""

def test_import_scheduled_tasks():
    try:
        import app.services.scheduled_tasks as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar scheduled_tasks: {e}"
