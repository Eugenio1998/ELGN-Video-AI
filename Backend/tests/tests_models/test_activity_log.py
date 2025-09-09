from app.models.activity_log import ActivityLog

def test_activity_log_model():
    log = ActivityLog(user_id=1, action="login")
    assert log.action == "login"