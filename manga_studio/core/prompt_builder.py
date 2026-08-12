"""Constructeur déterministe de prompts IA en anglais pour le générateur vidéo."""

from typing import List, Optional
from manga_studio.core.models.character import CharacterBible


class PromptBuilder:
    """Compose les prompts IA en anglais avec les attributs visuels verrouillés et le suffixe de style."""

    @staticmethod
    def build_prompt(
        action_description_en: str,
        decor_en: str,
        camera_plan_en: str,
        character_ids_present: List[str],
        character_bible: CharacterBible,
        style_suffix: str = "epic anime style, consistent character design, cinematic composition, no text artifacts"
    ) -> str:
        """Assemble un prompt d'inférence vidéo cohérent et enrichi."""
        parts = [action_description_en.strip()]

        # Insertion des descriptions physiques des personnages présents
        char_descriptions = []
        for cid in character_ids_present:
            try:
                char = character_bible.get_character(cid)
                phys = char.description_physique
                acc = ", ".join(phys.accessoires_signature) if phys.accessoires_signature else ""
                acc_clause = f", carrying {acc}" if acc else ""
                desc = (
                    f"{char.nom} ({phys.silhouette}, {phys.peau} skin, {phys.visage}, "
                    f"{phys.coiffure}, wearing {phys.tenue}{acc_clause})"
                )
                char_descriptions.append(desc)
            except KeyError:
                continue

        if char_descriptions:
            parts.append(". ".join(char_descriptions) + ".")

        if decor_en:
            parts.append(decor_en.strip() + ".")

        if camera_plan_en:
            parts.append(camera_plan_en.strip() + ".")

        if style_suffix:
            parts.append(style_suffix.strip())

        full_prompt = " ".join(parts)
        # Nettoyage des doubles espaces et points consécutifs
        import re
        full_prompt = re.sub(r"\s+", " ", full_prompt)
        full_prompt = re.sub(r"\.\s*\.", ".", full_prompt)
        return full_prompt.strip()
