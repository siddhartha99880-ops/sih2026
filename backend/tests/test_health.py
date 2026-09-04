from fastapi.testclient import TestClient

from app.main import app


def test_health_contract() -> None:
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["environment"] == "development"
    assert response.json()["status"] in {"ok", "degraded"}
    assert response.json()["database"] in {"ready", "unavailable"}