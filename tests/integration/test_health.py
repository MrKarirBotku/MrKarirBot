from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint():
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]


def test_telegram_webhook_rejects_missing_secret(monkeypatch) -> None:
    from app.core.config import get_settings

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "expected-secret")
    get_settings.cache_clear()
    try:
        client = TestClient(create_app())
        response = client.post("/api/v1/telegram/webhook", json={})
        assert response.status_code == 403
    finally:
        get_settings.cache_clear()


def test_public_website_and_assets() -> None:
    client = TestClient(create_app())

    homepage = client.get("/")
    stylesheet = client.get("/assets/styles.css")

    assert homepage.status_code == 200
    assert "MrKarir AI" in homepage.text
    assert stylesheet.status_code == 200
    assert "--green" in stylesheet.text
