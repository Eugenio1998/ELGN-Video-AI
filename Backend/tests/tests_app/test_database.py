"""
Teste de importação do módulo: database
"""

def test_import_database():
    try:
        import app.database as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar database: {e}"
