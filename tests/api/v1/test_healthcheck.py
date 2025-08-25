from fastapi.testclient import TestClient

from todo_app.main import app

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/api/v1/healthcheck")

    assert response.json() == "お疲れ様です！！"
    assert response.status_code == 200
