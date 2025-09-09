import pytest
from app.utils import video_tools

def test_check_dependencies():
    with pytest.raises(Exception):
        video_tools._check_file_exists("arquivo_inexistente.mp4")
