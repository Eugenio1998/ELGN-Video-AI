"""
Teste de importação do módulo: startup
"""

def test_import_startup():
    try:
        import app.startup as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar startup: {e}"
