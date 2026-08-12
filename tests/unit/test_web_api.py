"""Tests unitaires pour l'API REST et le tableau de bord FastAPI."""

import importlib

from fastapi.testclient import TestClient

api_module = importlib.import_module("manga_studio.api.app")
client = TestClient(api_module.app)


class FakeJob:
    id = "job-test-123"


def test_api_status_endpoint():
    """Vérifie l'endpoint de statut général."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["gpu_ceiling_gb"] == 22.0
    assert data["job_queue"] == "redis-rq"
    assert res.headers["X-Request-ID"]


def test_api_dashboard_html():
    """Vérifie que la route racine renvoie le tableau de bord HTML."""
    res = client.get("/")
    assert res.status_code == 200
    assert "MangaTok Studio" in res.text
    assert "Mode « Conte animé »" in res.text


def test_api_generate_enqueues_a_job(monkeypatch):
    """La requête HTTP retourne rapidement un job au lieu d'exécuter le pipeline."""
    monkeypatch.setattr(api_module, "enqueue_generation", lambda payload: FakeJob())
    payload = {
        "tale_text": "Râ monta dans sa barque céleste.\n\nLes dieux applaudirent avec ferveur.",
        "story_id": "api_test_story",
        "profile": "research",
        "territory": "EU",
    }

    res = client.post("/api/generate", json=payload)

    assert res.status_code == 202
    assert res.json() == {
        "job_id": "job-test-123",
        "status": "queued",
        "story_id": "api_test_story",
        "status_url": "/api/jobs/job-test-123",
    }


def test_get_generation_job_returns_serialized_status(monkeypatch):
    expected = {"job_id": "job-test-123", "status": "running", "progress": 5}
    monkeypatch.setattr(api_module, "get_job", lambda job_id: FakeJob())
    monkeypatch.setattr(api_module, "job_response", lambda job: expected)

    res = client.get("/api/jobs/job-test-123")

    assert res.status_code == 200
    assert res.json() == expected
