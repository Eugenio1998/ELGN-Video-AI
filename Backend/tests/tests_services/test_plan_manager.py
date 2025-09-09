"""
Teste de importação e estrutura para o serviço: plan_manager
"""

def test_import_plan_manager():
    try:
        import app.services.plan_manager as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar plan_manager: {e}"
