from app.utils import utc_now, format_timestamp

def test_format_timestamp():
    now = utc_now()
    formatted = format_timestamp(now)
    assert isinstance(formatted, str)
