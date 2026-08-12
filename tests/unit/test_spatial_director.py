"""Tests unitaires pour le directeur spatial et la composition de scènes."""

from pathlib import Path
from manga_studio.adapters.character.rule_based_character_extractor import RuleBasedCharacterExtractorAdapter
from manga_studio.core.spatial_director import SceneSpatialDirector


def test_spatial_director_single_character():
    """Vérifie le positionnement centré pour un personnage unique."""
    extractor = RuleBasedCharacterExtractorAdapter()
    bible = extractor.extract_character_bible("mythe", "Râ", [Path("personnage_01.png")])

    placements = SceneSpatialDirector.arrange_scene(["ra"], bible)
    assert len(placements) == 1
    assert placements[0].horizontal_position == "center"
    assert placements[0].depth_layer == "foreground"

    clause = SceneSpatialDirector.compile_spatial_prompt_clause(placements)
    assert "[Spatial Arrangement: ra positioned on the center" in clause


def test_spatial_director_three_characters():
    """Vérifie le positionnement étagé pour 3 personnages ou plus."""
    extractor = RuleBasedCharacterExtractorAdapter()
    bible = extractor.extract_character_bible("mythe", "conte", [Path("p1.png"), Path("p2.png"), Path("p3.png")])

    placements = SceneSpatialDirector.arrange_scene(["ra", "gardien_02", "personnage_03"], bible)
    assert len(placements) == 3
    assert placements[0].depth_layer == "foreground"
    assert placements[1].depth_layer == "midground"
    assert placements[2].depth_layer == "background"
