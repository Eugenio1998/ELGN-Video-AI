"""
Teste de importação e estrutura para o serviço: file_cleaner
"""

def test_import_file_cleaner():
    try:
        import app.services.file_cleaner as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar file_cleaner: {e}"
