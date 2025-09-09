from app.models.image import Image

def test_image_model():
    image = Image(user_id=1, image_url="http://example.com/image.png")
    assert image.image_url == "http://example.com/image.png"