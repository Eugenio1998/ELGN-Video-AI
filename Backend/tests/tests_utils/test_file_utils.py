import os
from app.utils import file_utils

def test_generate_and_remove_temp_file():
    path = file_utils.generate_temp_file_path("test.txt")
    assert "test.txt" in path
    assert os.path.isdir(os.path.dirname(path))
    file_utils.remove_file(path)  # não dará erro mesmo se não existir
