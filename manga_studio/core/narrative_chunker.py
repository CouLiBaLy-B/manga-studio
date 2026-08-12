"""Découpage narratif et gestionnaire de mémoire de continuité pour contes longs."""

import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.storyboard import Storyboard, StoryboardSegment


class NarrativeChunk(BaseModel):
    """Segment ou chapitre d'un conte volumineux."""
    chunk_index: int
    title: str
    paragraphs: List[str]
    context_summary: str
    characters_involved: List[str]


class ContinuityMemory(BaseModel):
    """Mémoire de continuité conservée entre les blocs narratifs."""
    last_scene_id: Optional[str] = None
    last_emotion: str = "neutre"
    last_decor: str = ""
    last_action_summary: str = ""
    active_character_ids: List[str] = Field(default_factory=list)


class NarrativeChunker:
    """Découpe les contes volumineux en unités narratives tout en préservant la mémoire globale."""

    @staticmethod
    def chunk_tale(
        tale_text: str,
        character_bible: CharacterBible,
        paragraphs_per_chunk: int = 3
    ) -> List[NarrativeChunk]:
        """Découpe le texte en blocs narratifs logiques."""
        raw_paras = [p.strip() for p in tale_text.split("\n\n") if p.strip()]
        if not raw_paras:
            raw_paras = [p.strip() for p in tale_text.split("\n") if p.strip()]

        chunks: List[NarrativeChunk] = []
        for i in range(0, len(raw_paras), paragraphs_per_chunk):
            chunk_paras = raw_paras[i:i + paragraphs_per_chunk]
            chunk_idx = (i // paragraphs_per_chunk) + 1
            chunk_text = " ".join(chunk_paras).lower()

            # Identification des personnages du chunk
            involved = []
            for char in character_bible.characters:
                if char.nom.lower() in chunk_text or char.character_id in chunk_text:
                    involved.append(char.character_id)
            if not involved and character_bible.characters:
                involved.append(character_bible.characters[0].character_id)

            summary = f"Arc narratif {chunk_idx}: {chunk_paras[0][:80]}..."
            chunk = NarrativeChunk(
                chunk_index=chunk_idx,
                title=f"Partie {chunk_idx}",
                paragraphs=chunk_paras,
                context_summary=summary,
                characters_involved=involved
            )
            chunks.append(chunk)

        return chunks

    @staticmethod
    def merge_and_reorder_segments(
        segment_groups: List[List[StoryboardSegment]],
        story_id: str,
        title: str = ""
    ) -> Storyboard:
        """Fusionne et réordonne de manière déterministe les segments issus de plusieurs chunks."""
        flat_segments: List[StoryboardSegment] = []
        current_order = 1

        for group in segment_groups:
            for seg in group:
                updated_seg = seg.model_copy(
                    update={
                        "ordre": current_order,
                        "scene_id": f"scene_{current_order:03d}"
                    }
                )
                flat_segments.append(updated_seg)
                current_order += 1

        return Storyboard(
            schema_version="1.0",
            story_id=story_id,
            title=title or f"Conte animé : {story_id}",
            segments=flat_segments
        )
