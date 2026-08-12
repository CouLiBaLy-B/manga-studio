"""Tests unitaires pour l'éditeur de Storyboard (Human-in-the-Loop) via l'API REST."""

import json
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from manga_studio.api.app import app

client = TestClient(app)


def test_update_segment_endpoint():
    """Vérifie la mise à jour unitaire d'un segment via PUT /api/runs/{story_id}/segments/{scene_id}."""
    update_payload = {
        "titre": "Titre Révisé par l'Auteur",
        "frame": "Action modifiée en direct",
        "prompt_ia": "Updated prompt in English. epic anime style",
        "duree_s": 7.0,
        "emotion": "mystique"
    }

    res = client.put("/api/runs/conte/segments/scene_001", json=update_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "UPDATED"
    assert data["segment"]["titre"] == "Titre Révisé par l'Auteur"


def test_reorder_segments_endpoint():
    """Vérifie le réordonnancement des segments du storyboard."""
    reorder_payload = {
        "scene_ids_in_order": ["scene_002", "scene_001", "scene_003"]
    }
    res = client.post("/api/runs/conte/reorder", json=reorder_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "REORDERED"
    assert data["total_segments"] == 3
