# 📁 tests/tests_dependencies/test_access_control.py

import pytest
from fastapi import HTTPException
from app.dependencies.access_control import (
    require_paid_plan,
    require_premium_plan,
    require_admin_role,
    require_active_subscription,
)
from app.models.user import User, UserRole
from app.models.plan import Plan
from app.models.subscription import Subscription


def make_user(plan_name=None, role=UserRole.USER, subscription_status="active"):
    return User(
        username="test_user",
        plan=Plan(name=plan_name) if plan_name else None,
        role=role,
        subscription=Subscription(status=subscription_status),
    )


def test_require_paid_plan_accepts_pro_user():
    user = make_user(plan_name="Pro")
    assert require_paid_plan(user) == user


def test_require_paid_plan_denies_basic_user():
    user = make_user(plan_name="Basic")
    with pytest.raises(HTTPException) as exc:
        require_paid_plan(user)
    assert exc.value.status_code == 403


def test_require_premium_plan_accepts_premium_user():
    user = make_user(plan_name="Premium")
    assert require_premium_plan(user) == user


def test_require_premium_plan_denies_pro_user():
    user = make_user(plan_name="Pro")
    with pytest.raises(HTTPException):
        require_premium_plan(user)


def test_require_admin_role_accepts_admin():
    user = make_user(role=UserRole.ADMIN)
    assert require_admin_role(user) == user


def test_require_admin_role_denies_user():
    user = make_user(role=UserRole.USER)
    with pytest.raises(HTTPException):
        require_admin_role(user)


def test_require_active_subscription_accepts_active():
    user = make_user(subscription_status="active")
    assert require_active_subscription(user) == user


def test_require_active_subscription_denies_inactive():
    user = make_user(subscription_status="inactive")
    with pytest.raises(HTTPException):
        require_active_subscription(user)
