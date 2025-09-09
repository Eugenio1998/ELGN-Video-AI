"""
Teste de importação e estrutura para o serviço: security
"""

def test_import_security():
    try:
        import app.services.security as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar security: {e}"
