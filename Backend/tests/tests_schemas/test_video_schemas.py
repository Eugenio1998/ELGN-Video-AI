# 📄 tests/tests_schemas/test_video_schemas.py

from app.schemas.video import VideoCreate, VideoOut
from datetime import datetime

def test_video_create():
    video = VideoCreate(original_filename="video.mp4")
    assert video.original_filename == "video.mp4"

def test_video_out_schema():
    video = VideoOut(
        id=1,
        user_id=1,
        processed_url="https://cdn.elgn.ai/processed/video1.mp4",
        created_at=datetime.utcnow(),
        original_filename="video.mp4",
        duration=120.5,
        size_bytes=1024000,
        format="mp4",
        status="completed"
    )
    assert video.status == "completed"
