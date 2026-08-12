"""Tests unitaires pour l'ordonnancement des segments et la continuité narrative."""

from pathlib import Path
from manga_studio.adapters.character.rule_based_character_extractor import RuleBasedCharacterExtractorAdapter
from manga_studio.adapters.storyboard.local_fallback_adapter import LocalStoryboardFallbackAdapter
from manga_studio.core.models.config import TalePipelineConfig


def test_storyboard_generation_from_tale_text():
    """Vérifie la génération d'un storyboard ordonné et tracé à partir d'un conte textuel."""
    tale_text = """Au commencement des temps, Râ régnait sur l'Égypte avec splendeur.

Les gardiens s'inclinèrent : « La route du ciel est prête ».

La barque d'or quitta doucement la rive pour s'élever dans les constellations."""

    extractor = RuleBasedCharacterExtractorAdapter()
    bible = extractor.extract_character_bible("mythe_ra", tale_text, [Path("personnage_01.png")])
    
    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages"),
        style_suffix="epic anime style, consistent character design, no text artifacts"
    )

    adapter = LocalStoryboardFallbackAdapter()
    storyboard = adapter.generate_storyboard("mythe_ra", tale_text, bible, config)

    assert len(storyboard.segments) == 3
    for idx, seg in enumerate(storyboard.segments, start=1):
        assert seg.ordre == idx
        assert seg.scene_id == f"scene_{idx:03d}"
        assert len(seg.source_refs) >= 1
        assert seg.source_refs[0].paragraph_index == idx
        assert "epic anime style" in seg.prompt_ia
        assert seg.duree_s > 0
