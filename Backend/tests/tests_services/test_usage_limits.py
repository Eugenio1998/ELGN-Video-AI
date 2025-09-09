"""
Teste de importação e estrutura para o serviço: usage_limits
"""

def test_import_usage_limits():
    try:
        import app.services.usage_limits as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar usage_limits: {e}"
