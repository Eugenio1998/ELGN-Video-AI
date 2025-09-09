from app.models.usage_log import UsageLog

def test_usage_log_model():
    log = UsageLog(user_id=1, action="generate", resource_type="video")
    assert log.resource_type == "video"