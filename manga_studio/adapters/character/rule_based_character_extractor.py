"""Adaptateur d'extraction de fiches personnages canoniques."""

import hashlib
from pathlib import Path
from typing import Dict, List
from manga_studio.core.models.character import (
    CharacterBible,
    CharacterSheet,
    PhysicalDescription,
    SuggestedVoice,
)
from manga_studio.core.ports.character_extractor import CharacterSheetExtractorPort


class RuleBasedCharacterExtractorAdapter(CharacterSheetExtractorPort):
    """Adaptateur déterministe extrayant les fiches canoniques et garantissant le verrouillage immuable."""

    def extract_character_bible(
        self,
        story_id: str,
        tale_text: str,
        image_paths: List[Path],
        locked: bool = True
    ) -> CharacterBible:
        """Extrait la bible canonique à partir des images et du texte du conte."""
        characters: List[CharacterSheet] = []

        # Création d'une table d'association image -> identifiant stable
        sorted_images = sorted(image_paths, key=lambda p: p.name)

        if not sorted_images:
            # Fallback par défaut si aucune image fournie
            sorted_images = [Path("personnage_01.png")]

        # Détection d'entités classiques (ex: Râ, Gardien, Isis, Anubis, etc.)
        text_lower = tale_text.lower()

        for idx, img_path in enumerate(sorted_images, start=1):
            stem = img_path.stem.lower()

            if "ra" in stem or "râ" in text_lower and idx == 1:
                cid = "ra"
                nom = "Râ"
                role = "dieu solaire, personnage principal"
                phys = PhysicalDescription(
                    silhouette="grande silhouette royale et imposante",
                    visage="traits adultes nobles, regard calme et rayonnant",
                    peau="brun chaud",
                    coiffure="coiffe royale dorée avec disque solaire",
                    tenue="robe blanche et or",
                    couleurs_hex=["#F4C542", "#F7F2E8", "#8A5A2B"],
                    accessoires_signature=["disque solaire", "sceptre was"]
                )
                voice = SuggestedVoice(langue="français", ton="grave, posé, bienveillant")
                traits = ["solennel", "protecteur", "sage"]
            elif "gardien" in stem or "gardien" in text_lower:
                cid = f"gardien_{idx:02d}"
                nom = f"Gardien {idx:02d}"
                role = "gardien de la barque solaire"
                phys = PhysicalDescription(
                    silhouette="silhouette athlétique et vigilante",
                    visage="traits concentrés, regard loyal",
                    peau="cuivré",
                    coiffure="nénès égyptien rayé bleu et or",
                    tenue="pagne bleu et armure de cuir",
                    couleurs_hex=["#1E3A8A", "#D97706", "#FFFFFF"],
                    accessoires_signature=["lance cérémonielle", "bouclier"]
                )
                voice = SuggestedVoice(langue="français", ton="ferme, loyal, respectueux")
                traits = ["loyal", "vigilant", "discipliné"]
            else:
                # Personnage générique déduit de l'image
                cid = f"personnage_{idx:02d}"
                nom = f"Personnage {idx:02d}"
                role = "protagoniste du conte"
                phys = PhysicalDescription(
                    silhouette="silhouette animée expressive",
                    visage="traits fins, regard expressif",
                    peau="naturel",
                    coiffure="cheveux soignés",
                    tenue="tunique traditionnelle",
                    couleurs_hex=["#2563EB", "#F3F4F6"],
                    accessoires_signature=["insigne narratif"]
                )
                voice = SuggestedVoice(langue="français", ton="naturel et expressif")
                traits = ["déterminé", "émissaire"]

            sheet = CharacterSheet(
                character_id=cid,
                nom=nom,
                role=role,
                source_image_ids=[img_path.name],
                description_physique=phys,
                traits_caractere=traits,
                voix_suggeree=voice,
                style_constraints=[
                    "epic anime style",
                    "consistent character design",
                    "no text artifacts"
                ],
                locked=True
            )
            characters.append(sheet)

        return CharacterBible(
            story_id=story_id,
            characters=characters,
            version="1.0",
            locked=True
        )
