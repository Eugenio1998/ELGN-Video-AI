"""
Teste de importação e estrutura para o serviço: editor
"""

def test_import_editor():
    try:
        import app.services.editor as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar editor: {e}"
