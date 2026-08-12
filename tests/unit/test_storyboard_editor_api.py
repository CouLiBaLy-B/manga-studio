"""Tests hermétiques de l'éditeur de Storyboard via l'API REST."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from manga_studio.api.app import app
from manga_studio.core.models.storyboard import Storyboard, StoryboardSegment


client = TestClient(app)


@pytest.fixture(autouse=True)
def storyboard_run(isolated_api_output_root: Path) -> None:
    """Crée un storyboard temporaire, indépendant de demo_output et de l'ordre des tests."""
    segments = [
        StoryboardSegment(
            ordre=index,
            scene_id=f"scene_{index:03d}",
            titre=f"Scène {index}",
            frame=f"Action de test {index}",
            prompt_ia=f"A valid cinematic test prompt for scene {index}.",
            decor="Décor de test",
        )
        for index in range(1, 4)
    ]
    storyboard = Storyboard(story_id="conte", title="Conte de test", segments=segments)
    run_dir = isolated_api_output_root / "conte"
    run_dir.mkdir(parents=True)
    (run_dir / "storyboard.validated.json").write_text(
        storyboard.model_dump_json(indent=2), encoding="utf-8"
    )


def test_update_segment_endpoint():
    """Vérifie la mise à jour unitaire d'un segment via PUT."""
    update_payload = {
        "titre": "Titre Révisé par l'Auteur",
        "frame": "Action modifiée en direct",
        "prompt_ia": "Updated prompt in English. epic anime style",
        "duree_s": 7.0,
        "emotion": "mystique",
    }

    res = client.put("/api/runs/conte/segments/scene_001", json=update_payload)

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "UPDATED"
    assert data["segment"]["titre"] == "Titre Révisé par l'Auteur"


def test_reorder_segments_endpoint():
    """Vérifie le réordonnancement complet des segments."""
    res = client.post(
        "/api/runs/conte/reorder",
        json={"scene_ids_in_order": ["scene_002", "scene_001", "scene_003"]},
    )

    assert res.status_code == 200
    assert res.json() == {"status": "REORDERED", "total_segments": 3}


@pytest.mark.parametrize(
    "scene_ids_in_order",
    [
        ["scene_001", "scene_002"],
        ["scene_001", "scene_002", "unknown"],
        ["scene_001", "scene_001", "scene_003"],
    ],
)
def test_reorder_rejects_incomplete_unknown_or_duplicate_scene_ids(scene_ids_in_order: list[str]):
    """Un payload de réordonnancement doit être une permutation exacte des scènes."""
    res = client.post("/api/runs/conte/reorder", json={"scene_ids_in_order": scene_ids_in_order})

    assert res.status_code == 422
