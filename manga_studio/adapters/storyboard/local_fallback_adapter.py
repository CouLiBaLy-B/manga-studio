"""Adaptateur local de génération de Storyboard (Fallback souverain et hors-ligne)."""

import re
from typing import List
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    Storyboard,
    StoryboardSegment,
    TransitionConfig,
)
from manga_studio.core.ports.storyboard_llm import StoryboardLLMPort
from manga_studio.core.prompt_builder import PromptBuilder


class LocalStoryboardFallbackAdapter(StoryboardLLMPort):
    """Générateur de storyboard local, déterministe et conforme au schéma Pydantic."""

    def generate_storyboard(
        self,
        story_id: str,
        tale_text: str,
        character_bible: CharacterBible,
        config: TalePipelineConfig
    ) -> Storyboard:
        """Découpe le conte en paragraphes narratifs et génère les segments structurés."""
        paragraphs = [p.strip() for p in tale_text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in tale_text.split("\n") if p.strip()]

        if not paragraphs:
            paragraphs = ["Il était une fois dans l'Égypte antique un mythe grandiose."]

        segments: List[StoryboardSegment] = []
        cids = [c.character_id for c in character_bible.characters]
        primary_cid = cids[0] if cids else "ra"

        for idx, para in enumerate(paragraphs, start=1):
            scene_id = f"scene_{idx:03d}"
            
            # Détection de répliques entre guillemets (« ... » ou " ... ")
            dialogue_matches = re.findall(r'[«"]([^»"]+)[»"]', para)
            audio_items: List[AudioScriptItem] = []

            if dialogue_matches:
                for diag in dialogue_matches:
                    speaker = "Râ" if "râ" in para.lower() else ("Gardien" if "gardien" in para.lower() else "Narrateur")
                    audio_items.append(
                        AudioScriptItem(
                            speaker=speaker,
                            kind="dialogue",
                            text=diag.strip()
                        )
                    )
            else:
                # Narration par défaut
                short_narration = para[:120] + ("..." if len(para) > 120 else "")
                audio_items.append(
                    AudioScriptItem(
                        speaker="Narrateur",
                        kind="narration",
                        text=short_narration
                    )
                )

            # Attribution des personnages présents
            present = []
            para_lower = para.lower()
            for char in character_bible.characters:
                if char.nom.lower() in para_lower or char.character_id in para_lower:
                    present.append(char.character_id)
            if not present:
                present = [primary_cid]

            # Construction de l'action et du prompt IA en anglais
            titre = f"Scène {idx} — {para[:40]}..."
            frame_fr = f"Action du conte : {para[:150]}"
            
            action_en = f"Cinematic sequence depicting scene {idx} of the tale. The main figures perform their destined actions."
            if "soleil" in para_lower or "barque" in para_lower or "nuit" in para_lower:
                decor_en = "Starry night on the Nile river, mystical divine atmosphere"
                plan_en = "cinematic low angle, dramatic lighting"
                emotion = "épique"
            else:
                decor_en = "Ancient mythological realm with radiant atmospheric illumination"
                plan_en = "cinematic medium shot"
                emotion = "solennel"

            prompt_ia = PromptBuilder.build_prompt(
                action_description_en=action_en,
                decor_en=decor_en,
                camera_plan_en=plan_en,
                character_ids_present=present,
                character_bible=character_bible,
                style_suffix=config.style_suffix
            )

            seg = StoryboardSegment(
                ordre=idx,
                scene_id=scene_id,
                titre=titre,
                source_refs=[SourceRef(paragraph_index=idx, excerpt=para[:100])],
                frame=frame_fr,
                characters_present=present,
                reference_character_ids=present,
                audio_script=audio_items,
                prompt_ia=prompt_ia,
                duree_s=6.0,
                emotion=emotion,
                plan=plan_en,
                decor=decor_en,
                continuity_in=f"Début du segment narratif {idx}.",
                continuity_out=f"Fin du segment narratif {idx}, transition vers la suite.",
                transition=TransitionConfig(type="fade", duration_s=config.transition_duration_s)
            )
            segments.append(seg)

        return Storyboard(
            schema_version="1.0",
            story_id=story_id,
            title=f"Conte animé : {story_id}",
            segments=segments
        )
