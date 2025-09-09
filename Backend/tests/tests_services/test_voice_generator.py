"""
Teste de importação e estrutura para o serviço: voice_generator
"""

def test_import_voice_generator():
    try:
        import app.services.voice_generator as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar voice_generator: {e}"
