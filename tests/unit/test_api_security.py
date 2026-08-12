"""Tests de sécurité des garde-fous HTTP du lot 1."""

from fastapi.testclient import TestClient

from manga_studio.api.app import _run_dir, app


client = TestClient(app)


def test_protected_write_requires_a_valid_api_key(monkeypatch):
    monkeypatch.setenv("MANGA_STUDIO_API_KEY", "test-secret")

    missing = client.post("/api/runs/unknown/reorder", json={"scene_ids_in_order": []})
    invalid = client.post(
        "/api/runs/unknown/reorder",
        json={"scene_ids_in_order": []},
        headers={"X-API-Key": "invalid"},
    )

    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_invalid_story_id_is_rejected_before_path_construction():
    for story_id in ("../outside", "a/b", "", ".hidden"):
        response = client.get(f"/api/runs/{story_id}/bible")
        assert response.status_code in {404, 422}


def test_run_directory_stays_inside_the_output_root():
    run_directory = _run_dir("safe-run_42")
    assert run_directory.parent.name == "output"
    assert _run_dir("safe-run_42") == run_directory
