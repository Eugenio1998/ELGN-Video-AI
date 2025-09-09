from app.models.subscription import Subscription, PaymentStatusEnum

def test_subscription_model():
    subscription = Subscription(user_id=1, plan_id=2, payment_status=PaymentStatusEnum.PENDING)
    assert subscription.user_id == 1
    assert subscription.plan_id == 2
    assert subscription.payment_status == PaymentStatusEnum.PENDING