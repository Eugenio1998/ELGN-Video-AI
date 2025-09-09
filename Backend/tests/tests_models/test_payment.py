from app.models.payment import Payment, PaymentStatusEnum

def test_payment_model():
    payment = Payment(user_id=1, amount=49.99, status=PaymentStatusEnum.COMPLETED)
    assert payment.amount == 49.99
    assert payment.status == PaymentStatusEnum.COMPLETED