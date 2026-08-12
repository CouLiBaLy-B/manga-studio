"""Tests unitaires pour la sélection déterministe des images de référence."""

from pathlib import Path
from manga_studio.adapters.character.reference_selector_adapter import ReferenceSelectorAdapter
from manga_studio.adapters.character.rule_based_character_extractor import RuleBasedCharacterExtractorAdapter
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)


def test_reference_selector_active_characters():
    """Vérifie que seules les images des personnages actifs sont sélectionnées dans l'ordre."""
    extractor = RuleBasedCharacterExtractorAdapter()
    images = [Path("personnage_01.png"), Path("personnage_02.png")]
    bible = extractor.extract_character_bible("mythe", "Râ et le gardien", images)

    image_store_map = {
        "personnage_01.png": Path("/data/personnage_01.png"),
        "personnage_02.png": Path("/data/personnage_02.png"),
    }

    selector = ReferenceSelectorAdapter()

    # Scène 1 : Seul Râ est présent
    seg1 = StoryboardSegment(
        ordre=1,
        scene_id="scene_001",
        titre="Scène 1",
        source_refs=[],
        frame="Râ apparaît",
        characters_present=["ra"],
        reference_character_ids=["ra"],
        audio_script=[],
        prompt_ia="Ra stands proud. epic anime style",
        duree_s=5.0,
        emotion="épique",
        plan="medium",
        decor="palais",
        continuity_in="",
        continuity_out="",
        transition=TransitionConfig()
    )

    selected = selector.select_references_for_segment(seg1, bible, image_store_map, max_references=9)
    assert len(selected) == 1
    assert selected[0] == Path("/data/personnage_01.png")


def test_reference_selector_clamping_to_max():
    """Vérifie que la sélection est bornée au maximum configuré."""
    extractor = RuleBasedCharacterExtractorAdapter()
    images = [Path(f"personnage_{i:02d}.png") for i in range(1, 10)]
    bible = extractor.extract_character_bible("mythe", "conte", images)

    image_store_map = {f"personnage_{i:02d}.png": Path(f"/data/personnage_{i:02d}.png") for i in range(1, 10)}
    selector = ReferenceSelectorAdapter()

    seg = StoryboardSegment(
        ordre=1,
        scene_id="scene_001",
        titre="Scène avec foule",
        source_refs=[],
        frame="Foule de dieux",
        characters_present=[c.character_id for c in bible.characters],
        reference_character_ids=[c.character_id for c in bible.characters],
        audio_script=[],
        prompt_ia="Many gods gathered. epic anime style",
        duree_s=5.0,
        emotion="épique",
        plan="wide",
        decor="ciel",
        continuity_in="",
        continuity_out="",
        transition=TransitionConfig()
    )

    selected = selector.select_references_for_segment(seg, bible, image_store_map, max_references=4)
    assert len(selected) == 4
