from app.models.feedback import Feedback, FeedbackCategory

def test_feedback_model():
    feedback = Feedback(user_id=1, category=FeedbackCategory.APP, message="Ótimo software")
    assert feedback.category == FeedbackCategory.APP