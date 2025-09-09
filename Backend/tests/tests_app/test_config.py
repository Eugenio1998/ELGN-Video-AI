"""
Teste de importação do módulo: config
"""

def test_import_config():
    try:
        import app.config as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar config: {e}"
