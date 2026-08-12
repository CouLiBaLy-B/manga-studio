"""Tests unitaires pour l'évaluateur QC et la stratégie de régénération bornée (max 2 retries)."""

import tempfile
from pathlib import Path
from manga_studio.adapters.qc.clip_dino_qc_adapter import ClipOrDinoQualityEvaluatorAdapter
from manga_studio.adapters.qc.mock_qc_adapter import MockQualityEvaluatorAdapter
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)


def create_dummy_segment(scene_id: str = "scene_001") -> StoryboardSegment:
    return StoryboardSegment(
        ordre=1,
        scene_id=scene_id,
        titre="Scène test",
        source_refs=[],
        frame="Râ apparaît",
        characters_present=["ra"],
        reference_character_ids=["ra"],
        audio_script=[AudioScriptItem(speaker="Râ", kind="dialogue", text="Que la lumière soit.")],
        prompt_ia="Ra steps forward wearing golden robes. epic anime style",
        duree_s=5.0,
        emotion="épique",
        plan="medium",
        decor="palais",
        continuity_in="",
        continuity_out="",
        transition=TransitionConfig()
    )


def test_quality_evaluator_passed_report():
    """Vérifie l'évaluation positive d'un clip valide."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_clip:
        tmp_clip.write(b"\x00" * 1024)
        tmp_clip.flush()
        clip_path = Path(tmp_clip.name)

        config = TalePipelineConfig(
            story_path=Path("tests/fixtures/conte.txt"),
            characters_dir=Path("tests/fixtures/personnages"),
            qc_similarity_threshold=0.75
        )

        evaluator = ClipOrDinoQualityEvaluatorAdapter()
        seg = create_dummy_segment()
        report = evaluator.evaluate_clip(
            clip_path=clip_path,
            segment=seg,
            reference_images=[Path("tests/fixtures/personnages/personnage_01.png")],
            attempt=1,
            config=config
        )

        assert report.status == "passed"
        assert report.recommendation == "accept"
        assert report.visual_similarity.score >= 0.75
        assert report.duration_ok is True
        assert report.audio_present is True


def test_bounded_regeneration_retry_to_needs_review():
    """Vérifie la progression de retry : échec tentative 1 -> retry, échec tentative 3 -> needs_review."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_clip:
        clip_path = Path(tmp_clip.name)
        config = TalePipelineConfig(
            story_path=Path("tests/fixtures/conte.txt"),
            characters_dir=Path("tests/fixtures/personnages"),
            max_qc_retries=2
        )
        seg = create_dummy_segment()
        evaluator = MockQualityEvaluatorAdapter(force_status="failed", fixed_score=0.60)

        # Tentative 1 (essai initial) -> recommandation retry
        r1 = evaluator.evaluate_clip(clip_path, seg, [], attempt=1, config=config)
        assert r1.status == "failed"
        assert r1.recommendation == "retry"

        # Tentative 2 (1er retry) -> recommandation retry
        r2 = evaluator.evaluate_clip(clip_path, seg, [], attempt=2, config=config)
        assert r2.status == "failed"
        assert r2.recommendation == "retry"

        # Tentative 3 (2ème retry = max_retries atteint) -> recommandation flag_review
        r3 = evaluator.evaluate_clip(clip_path, seg, [], attempt=3, config=config)
        assert r3.status == "failed"
        assert r3.recommendation == "flag_review"
