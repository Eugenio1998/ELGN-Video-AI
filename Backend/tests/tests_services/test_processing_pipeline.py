"""
Teste de importação e estrutura para o serviço: processing_pipeline
"""

def test_import_processing_pipeline():
    try:
        import app.services.processing_pipeline as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar processing_pipeline: {e}"
