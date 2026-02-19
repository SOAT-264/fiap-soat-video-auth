from fastapi.testclient import TestClient

from auth_service.infrastructure.adapters.input.api.main import create_app


def test_health_and_ready_endpoints(monkeypatch):
    async def fake_init_db():
        return None

    monkeypatch.setattr("auth_service.infrastructure.adapters.input.api.main.init_db", fake_init_db)

    app = create_app()
    with TestClient(app) as client:
        health = client.get("/health")
        ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json() == {"status": "healthy", "service": "auth-service"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}
