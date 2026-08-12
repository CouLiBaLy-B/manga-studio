"""Test d'intégration End-to-End pour le mode « Conte animé »."""

import json
import tempfile
from pathlib import Path
from manga_studio.core.models.config import DeploymentProfile, TalePipelineConfig
from manga_studio.pipeline.runner import AnimatedTalePipelineRunner


def test_e2e_animated_tale_pipeline_execution():
    """Exécute l'intégralité du pipeline sur le conte fixture et vérifie l'arborescence de sortie."""
    story_fixture = Path("tests/fixtures/conte.txt")
    chars_fixture = Path("tests/fixtures/personnages")

    assert story_fixture.exists(), "Fixture conte.txt manquante"
    assert chars_fixture.exists(), "Fixture personnages manquante"

    with tempfile.TemporaryDirectory() as tmp_output:
        output_dir = Path(tmp_output)

        config = TalePipelineConfig(
            story_path=story_fixture,
            characters_dir=chars_fixture,
            output_dir=output_dir,
            profile=DeploymentProfile.RESEARCH,
            territory="EU",
            enable_bedrock=False,      # Fallback local souverain
            enable_h3_local=False,     # Utilisation du générateur mock
            max_reference_images=9,
            generate_subtitles=True
        )

        final_state = AnimatedTalePipelineRunner.run_pipeline(
            config=config,
            use_mock_video=True
        )

        # 1. Vérification de l'état final
        assert final_state["status"] in ("COMPLETED", "COMPLETED_WITH_WARNINGS")

        # 2. Vérification des artefacts générés
        bible_path = output_dir / "character_bible.json"
        assert bible_path.exists(), "character_bible.json manquant"
        bible_data = json.loads(bible_path.read_text(encoding="utf-8"))
        assert bible_data["locked"] is True
        assert len(bible_data["characters"]) >= 1

        storyboard_path = output_dir / "storyboard.json"
        assert storyboard_path.exists(), "storyboard.json manquant"

        val_storyboard_path = output_dir / "storyboard.validated.json"
        assert val_storyboard_path.exists(), "storyboard.validated.json manquant"
        sb_data = json.loads(val_storyboard_path.read_text(encoding="utf-8"))
        assert len(sb_data["segments"]) == 3

        # 3. Vérification des clips
        for idx in (1, 2, 3):
            clip_file = output_dir / "clips" / f"{idx:03d}.mp4"
            assert clip_file.exists(), f"Clip {idx:03d}.mp4 manquant"
            assert clip_file.stat().st_size > 0

        # 4. Vérification des rapports QC
        for idx in (1, 2, 3):
            qc_file = output_dir / "qc" / f"{idx:03d}.json"
            assert qc_file.exists(), f"Rapport QC {idx:03d}.json manquant"
            qc_data = json.loads(qc_file.read_text(encoding="utf-8"))
            assert qc_data["status"] in ("passed", "needs_review")

        # 5. Vérification des sous-titres
        srt_file = output_dir / "subtitles" / "conte.srt"
        ass_file = output_dir / "subtitles" / "conte.ass"
        assert srt_file.exists(), "conte.srt manquant"
        assert ass_file.exists(), "conte.ass manquant"

        # 6. Vérification du manifest et run report
        manifest_file = output_dir / "manifests" / "render_manifest.jsonl"
        report_file = output_dir / "manifests" / "run_report.json"
        assert manifest_file.exists(), "render_manifest.jsonl manquant"
        assert report_file.exists(), "run_report.json manquant"

        report_data = json.loads(report_file.read_text(encoding="utf-8"))
        assert report_data["stats"]["total_segments"] == 3
        assert len(report_data["licenses"]) > 0

        # 7. Vérification de la vidéo finale assemblée
        final_video = output_dir / "conte_final.mp4"
        assert final_video.exists(), "conte_final.mp4 manquant"
        assert final_video.stat().st_size > 0
