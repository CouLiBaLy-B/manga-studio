"""Tests unitaires pour l'API REST et le tableau de bord FastAPI."""

from fastapi.testclient import TestClient
from manga_studio.api.app import app

client = TestClient(app)


def test_api_status_endpoint():
    """Vérifie l'endpoint de statut général."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["gpu_ceiling_gb"] == 22.0


def test_api_dashboard_html():
    """Vérifie que la route racine renvoie le tableau de bord HTML."""
    res = client.get("/")
    assert res.status_code == 200
    assert "MangaTok Studio" in res.text
    assert "Mode « Conte animé »" in res.text


def test_api_generate_endpoint():
    """Vérifie le déclenchement d'un run via l'API REST."""
    payload = {
        "tale_text": "Râ monta dans sa barque céleste.\n\nLes dieux applaudirent avec ferveur.",
        "story_id": "api_test_story",
        "profile": "research",
        "territory": "EU"
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["story_id"] == "api_test_story"
    assert data["status"] in ("COMPLETED", "COMPLETED_WITH_WARNINGS")
