"""
Teste de importação do módulo: main_log_scheduler
"""

def test_import_main_log_scheduler():
    try:
        import importlib.util

        spec = importlib.util.find_spec("app.main_log_scheduler")
        assert spec is not None
    except Exception as e:
        assert False, f"Erro ao localizar main_log_scheduler: {e}"
