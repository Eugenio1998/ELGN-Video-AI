from app.models.audio import Audio

def test_audio_model():
    audio = Audio(user_id=1, filename="audio.mp3")
    assert audio.filename == "audio.mp3"