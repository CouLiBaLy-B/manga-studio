"""Tests unitaires pour la validation Pydantic du Storyboard et le respect du schéma."""

import pytest
from pydantic import ValidationError
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    Storyboard,
    StoryboardSegment,
    TransitionConfig,
)


def create_sample_segment(ordre: int, scene_id: str = "scene_001") -> StoryboardSegment:
    """Génère un segment valide pour tests."""
    return StoryboardSegment(
        ordre=ordre,
        scene_id=scene_id,
        titre="Scène de test",
        source_refs=[SourceRef(paragraph_index=1, excerpt="Extrait narratif")],
        frame="Râ monte à bord de la barque solaire.",
        characters_present=["ra"],
        reference_character_ids=["ra"],
        audio_script=[AudioScriptItem(speaker="Gardien", kind="dialogue", text="La route du ciel est prête.")],
        prompt_ia="Ra steps onto the solar boat. Warm brown skin, golden royal robes, starry night on the Nile.",
        duree_s=6.0,
        emotion="épique",
        plan="cinematic low angle",
        decor="bord du Nil, nuit étoilée",
        continuity_in="Arrivée des personnages.",
        continuity_out="Départ de la barque.",
        transition=TransitionConfig(type="fade", duration_s=0.3)
    )


def test_storyboard_valid_schema():
    """Vérifie la validation d'un storyboard complet et ordonné."""
    seg1 = create_sample_segment(1, "scene_001")
    seg2 = create_sample_segment(2, "scene_002")
    
    storyboard = Storyboard(
        schema_version="1.0",
        story_id="mythe-ra",
        title="Le Mythe de Râ",
        segments=[seg1, seg2]
    )
    assert storyboard.schema_version == "1.0"
    assert len(storyboard.segments) == 2
    assert storyboard.total_duration_s == 12.0


def test_storyboard_invalid_order_rejected():
    """Vérifie que des segments dans le désordre sont rejetés."""
    seg1 = create_sample_segment(2, "scene_001")
    seg2 = create_sample_segment(1, "scene_002")
    
    with pytest.raises(ValidationError):
        Storyboard(
            schema_version="1.0",
            story_id="mythe-ra",
            segments=[seg1, seg2]
        )


def test_storyboard_duplicate_scene_id_rejected():
    """Vérifie le rejet d'identifiants de scène dupliqués."""
    seg1 = create_sample_segment(1, "scene_001")
    seg2 = create_sample_segment(2, "scene_001")  # Même scene_id
    
    with pytest.raises(ValidationError):
        Storyboard(
            schema_version="1.0",
            story_id="mythe-ra",
            segments=[seg1, seg2]
        )
