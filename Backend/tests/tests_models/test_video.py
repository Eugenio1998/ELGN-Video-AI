from app.models.video import Video, VideoStatus

def test_video_model():
    video = Video(user_id=1, title="Teste", original_filename="original.mp4", status=VideoStatus.PENDING)
    assert video.user_id == 1
    assert video.title == "Teste"
    assert video.status == VideoStatus.PENDING