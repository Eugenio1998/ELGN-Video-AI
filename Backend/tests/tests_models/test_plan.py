from app.models.plan import Plan

def test_plan_model():
    plan = Plan(name="Pro", description="Plano Pro", price=25.0, is_active=True)
    assert plan.name == "Pro"
    assert plan.price == 25.0
    assert plan.is_active is True