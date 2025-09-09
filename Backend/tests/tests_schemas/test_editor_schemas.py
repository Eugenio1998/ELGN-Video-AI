from app.schemas.editor import CutRequest, CutResponse, MultipleCutRequest
import pytest

def test_cut_request_valid():
    cut = CutRequest(start_time=5.5, end_time=10.0)
    assert cut.start_time == 5.5
    assert cut.end_time == 10.0

def test_cut_request_invalid_times():
    with pytest.raises(ValueError):
        CutRequest(start_time=12.0, end_time=5.0)

def test_multiple_cut_request():
    cuts = [
        CutRequest(start_time=0, end_time=5),
        CutRequest(start_time=10, end_time=15)
    ]
    multiple = MultipleCutRequest(cuts=cuts)
    assert len(multiple.cuts) == 2

def test_cut_response():
    url = "https://cdn.elgn.ai/cortes/video123.mp4"
    response = CutResponse(output_url=url)
    assert str(response.output_url) == url  # ✅ Converte HttpUrl em str
