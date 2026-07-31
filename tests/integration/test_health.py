from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint():
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_public_website_and_assets() -> None:
    client = TestClient(create_app())

    homepage = client.get("/")
    stylesheet = client.get("/assets/styles.css")

    assert homepage.status_code == 200
    assert "MrKarir AI" in homepage.text
    assert stylesheet.status_code == 200
    assert "--green" in stylesheet.text
