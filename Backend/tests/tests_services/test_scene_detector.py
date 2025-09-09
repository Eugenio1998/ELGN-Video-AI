"""
Teste de importação e estrutura para o serviço: scene_detector
"""

def test_import_scene_detector():
    try:
        import app.services.scene_detector as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar scene_detector: {e}"
