"""Tests unitaires pour le découpage narratif des contes longs et la mémoire de continuité."""

from pathlib import Path
from manga_studio.adapters.character.rule_based_character_extractor import RuleBasedCharacterExtractorAdapter
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)
from manga_studio.core.narrative_chunker import NarrativeChunker


def test_narrative_chunker_multi_arc_splitting():
    """Vérifie le découpage d'un conte volumineux en arcs narratifs cohérents."""
    long_tale = "\n\n".join([f"Paragraphe numéro {i} relatant les aventures de Râ." for i in range(1, 10)])
    
    extractor = RuleBasedCharacterExtractorAdapter()
    bible = extractor.extract_character_bible("long_myth", long_tale, [Path("personnage_01.png")])

    chunks = NarrativeChunker.chunk_tale(
        tale_text=long_tale,
        character_bible=bible,
        paragraphs_per_chunk=3
    )

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 1
    assert len(chunks[0].paragraphs) == 3
    assert "ra" in chunks[0].characters_involved


def test_merge_and_reorder_segments():
    """Vérifie la fusion et le réordonnancement global des segments issus de multiples chunks."""
    seg1 = StoryboardSegment(
        ordre=1, scene_id="scene_001", titre="Scène 1", source_refs=[],
        frame="F1", characters_present=["ra"], reference_character_ids=["ra"],
        audio_script=[], prompt_ia="Prompt 1. epic anime style", duree_s=5.0,
        emotion="épique", plan="medium", decor="palais", continuity_in="",
        continuity_out="", transition=TransitionConfig()
    )
    seg2 = StoryboardSegment(
        ordre=1, scene_id="scene_001", titre="Scène 2", source_refs=[],
        frame="F2", characters_present=["ra"], reference_character_ids=["ra"],
        audio_script=[], prompt_ia="Prompt 2. epic anime style", duree_s=6.0,
        emotion="épique", plan="medium", decor="ciel", continuity_in="",
        continuity_out="", transition=TransitionConfig()
    )

    merged_sb = NarrativeChunker.merge_and_reorder_segments([[seg1], [seg2]], story_id="merged_story")
    assert len(merged_sb.segments) == 2
    assert merged_sb.segments[0].ordre == 1
    assert merged_sb.segments[0].scene_id == "scene_001"
    assert merged_sb.segments[1].ordre == 2
    assert merged_sb.segments[1].scene_id == "scene_002"
