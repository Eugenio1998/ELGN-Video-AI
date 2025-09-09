from app.utils import slugify, remove_accents

def test_slugify_basic():
    assert slugify("Título de Teste") == "titulo-de-teste"

def test_remove_accents():
    assert remove_accents("Edição de vídeo") == "Edicao de video"
