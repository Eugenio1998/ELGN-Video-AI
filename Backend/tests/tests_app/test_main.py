"""
Teste de importação do módulo: main
"""

def test_import_main():
    try:
        import app.main as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar main: {e}"
