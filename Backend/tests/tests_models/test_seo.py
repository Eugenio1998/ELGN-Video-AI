from app.models.seo import SEO

def test_seo_model():
    seo = SEO(user_id=1, video_title="Teste SEO")
    assert seo.video_title == "Teste SEO"