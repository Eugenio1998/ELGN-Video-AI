"""
Teste de importação e estrutura para o serviço: redis_cache
"""

def test_import_redis_cache():
    try:
        import app.services.redis_cache as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar redis_cache: {e}"
