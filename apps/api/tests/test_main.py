from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def production_client() -> TestClient:
    settings = get_settings().model_copy(update={"environment": "production"})
    return TestClient(create_app(settings))


def test_production_hides_the_interactive_docs() -> None:
    client = production_client()

    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404


def test_production_sends_a_strict_content_security_policy() -> None:
    response = production_client().get("/health")

    assert response.status_code == 200
    assert response.headers["Content-Security-Policy"].startswith("default-src 'none'")
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_development_keeps_the_docs(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
