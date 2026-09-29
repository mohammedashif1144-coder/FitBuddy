from sqlalchemy import select

from app.database import SessionLocal
from app.models import Plan, User


def test_user_and_plan_are_persisted(client):
    response = client.post(
        "/api/generate-workout",
        json={
            "user_id": "db-001",
            "name": "Taylor",
            "age": 28,
            "weight": 72,
            "goal": "muscle gain",
            "intensity": "medium",
        },
    )
    assert response.status_code == 200
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.user_id == "db-001"))
        assert user is not None
        plan = db.scalar(select(Plan).where(Plan.user_id == user.id))
        assert plan is not None
        assert plan.original_plan
        assert plan.nutrition_tip
