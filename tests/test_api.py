from unittest.mock import patch

from fastapi.testclient import TestClient

from url_summarizer.api.app import create_app
from url_summarizer.schemas import SummaryResult


@patch("url_summarizer.api.app.summarize_text")
@patch("url_summarizer.api.app.fetch_url_text")
def test_summarize_endpoint(mock_fetch, mock_summarize):
    mock_fetch.return_value = "Page content"
    mock_summarize.return_value = SummaryResult(
        title="Example Title",
        bullet_points=["a", "b", "c", "d", "e"],
    )

    client = TestClient(create_app())
    response = client.post(
        "/api/v1/summarize",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Example Title"
    assert len(data["bullet_points"]) == 5


def test_health_endpoint():
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_and_version_endpoints():
    client = TestClient(create_app())
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["docs"] == "/docs"

    version = client.get("/json/version")
    assert version.status_code == 200
    assert "version" in version.json()


def test_summarize_requires_api_key_when_configured():
    from url_summarizer.config import Settings, get_settings

    secured_settings = Settings(
        API_KEY="secret-key",
        GROQ_MODEL="openai/gpt-oss-20b",
        CORS_ORIGINS="*",
    )
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: secured_settings
    client = TestClient(app)

    response = client.post("/api/v1/summarize", json={"url": "https://example.com"})
    assert response.status_code == 401

    with patch("url_summarizer.api.app.fetch_url_text", return_value="content"), patch(
        "url_summarizer.api.app.summarize_text",
        return_value=SummaryResult(title="T", bullet_points=["a", "b", "c", "d", "e"]),
    ):
        response = client.post(
            "/api/v1/summarize",
            json={"url": "https://example.com"},
            headers={"X-API-Key": "secret-key"},
        )
    assert response.status_code == 200
