"""Tests unitaires pour la génération du Render Manifest JSONL et du Run Report."""

import json
import tempfile
from pathlib import Path
from manga_studio.adapters.storage.local_artifact_store_adapter import LocalArtifactStoreAdapter
from manga_studio.core.models.manifest import (
    CostReport,
    ExecutionStats,
    ManifestEvent,
    RunReport,
)


def test_artifact_store_and_manifest_jsonl():
    """Vérifie la persistance des événements dans render_manifest.jsonl."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        store = LocalArtifactStoreAdapter()
        root = store.initialize_store(Path(tmp_dir), "story_01")

        # Ajout d'événements
        ev1 = ManifestEvent(
            event_id="ev_001",
            step="ingestion",
            action="load_text",
            status="SUCCESS",
            details={"chars": 150}
        )
        ev2 = ManifestEvent(
            event_id="ev_002",
            step="storyboard",
            action="generate_scenes",
            status="SUCCESS",
            details={"scenes": 3}
        )

        store.append_manifest_event(ev1)
        store.append_manifest_event(ev2)

        manifest_file = root / "manifests" / "render_manifest.jsonl"
        assert manifest_file.exists()

        lines = manifest_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        data1 = json.loads(lines[0])
        assert data1["event_id"] == "ev_001"
        assert data1["step"] == "ingestion"


def test_run_report_generation():
    """Vérifie la structure et la conformité du run_report.json."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        store = LocalArtifactStoreAdapter()
        root = store.initialize_store(Path(tmp_dir), "story_01")

        report = RunReport(
            run_id="run_123",
            story_id="mythe-ra",
            status="COMPLETED",
            stats=ExecutionStats(total_segments=3, total_clips_generated=3, qc_passed_count=3),
            costs=CostReport(estimated_cost_usd=0.005, budget_cap_usd=2.0),
            licenses=[],
            output_video_path=str(root / "conte_final.mp4"),
            summary="Succès complet"
        )

        saved = store.save_run_report(report)
        assert saved.exists()

        loaded_data = json.loads(saved.read_text(encoding="utf-8"))
        assert loaded_data["run_id"] == "run_123"
        assert loaded_data["stats"]["total_segments"] == 3
