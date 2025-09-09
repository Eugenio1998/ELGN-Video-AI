"""
Teste de importação do módulo: tasks
"""

def test_import_tasks():
    try:
        import app.tasks as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar tasks: {e}"
