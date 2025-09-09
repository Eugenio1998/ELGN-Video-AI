from app.models.download import Download

def test_download_model():
    download = Download(user_id=1, video_id=5)
    assert download.video_id == 5