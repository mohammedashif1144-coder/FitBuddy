def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_generate_api_demo_mode(client):
    response = client.post(
        "/api/generate-workout",
        json={
            "user_id": "demo-001",
            "name": "Alex",
            "age": 25,
            "weight": 70,
            "goal": "general wellness",
            "intensity": "medium",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "demo-001"
    assert "Day 1" in data["plan"]
    assert data["demo_mode"] is True


def test_feedback_api(client):
    client.post(
        "/api/generate-workout",
        json={
            "user_id": "demo-002",
            "name": "Sam",
            "age": 30,
            "weight": 68,
            "goal": "endurance",
            "intensity": "low",
        },
    )
    response = client.post(
        "/api/submit-feedback",
        json={"user_id": "demo-002", "feedback": "Add more mobility work."},
    )
    assert response.status_code == 200
    assert "Add more mobility work." in response.json()["updated_plan"]


def test_validation_rejects_bad_age(client):
    response = client.post(
        "/api/generate-workout",
        json={
            "user_id": "bad-age",
            "name": "Alex",
            "age": 10,
            "weight": 70,
            "goal": "general wellness",
            "intensity": "medium",
        },
    )
    assert response.status_code == 422


def test_admin_requires_token(client):
    assert client.get("/view-all-users").status_code == 401
    assert client.get("/view-all-users?token=test-token").status_code == 200
