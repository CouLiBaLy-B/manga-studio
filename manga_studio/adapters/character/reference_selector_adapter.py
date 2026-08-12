"""Adaptateur pour la sélection déterministe des images de référence par scène."""

from pathlib import Path
from typing import Dict, List
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.storyboard import StoryboardSegment
from manga_studio.core.ports.reference_selector import ReferenceSelectorPort


class ReferenceSelectorAdapter(ReferenceSelectorPort):
    """Sélectionne de manière déterministe les images de référence pour les personnages actifs."""

    def select_references_for_segment(
        self,
        segment: StoryboardSegment,
        character_bible: CharacterBible,
        image_store_map: Dict[str, Path],
        max_references: int = 9
    ) -> List[Path]:
        """Retourne les chemins absolus des images de référence prioritaires."""
        selected_paths: List[Path] = []
        seen_paths = set()

        # Priorité aux personnages listés dans reference_character_ids, puis characters_present
        target_cids = list(dict.fromkeys(segment.reference_character_ids + segment.characters_present))

        for cid in target_cids:
            try:
                char_sheet = character_bible.get_character(cid)
                for img_name in sorted(char_sheet.source_image_ids):
                    if img_name in image_store_map:
                        img_path = image_store_map[img_name]
                        if img_path not in seen_paths:
                            selected_paths.append(img_path)
                            seen_paths.add(img_path)
                            if len(selected_paths) >= max_references:
                                return selected_paths
            except KeyError:
                continue

        # Si aucune référence spécifique n'a pu être résolue, fournir la première image disponible
        if not selected_paths and image_store_map:
            first_key = sorted(image_store_map.keys())[0]
            selected_paths.append(image_store_map[first_key])

        return selected_paths[:max_references]
