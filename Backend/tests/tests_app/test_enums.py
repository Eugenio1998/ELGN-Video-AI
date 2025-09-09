"""
Teste de importação do módulo: enums
"""

def test_import_enums():
    try:
        import app.enums as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar enums: {e}"
