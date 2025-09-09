"""
Teste de importação e estrutura para o serviço: transcription
"""

def test_import_transcription():
    try:
        import app.services.transcription as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar transcription: {e}"
