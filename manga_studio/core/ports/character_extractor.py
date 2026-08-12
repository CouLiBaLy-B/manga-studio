"""Port pour l'extraction et le verrouillage des fiches personnages canoniques."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from manga_studio.core.models.character import CharacterBible


class CharacterSheetExtractorPort(ABC):
    """Port d'extraction des fiches personnages à partir du conte et des images."""

    @abstractmethod
    def extract_character_bible(
        self,
        story_id: str,
        tale_text: str,
        image_paths: List[Path],
        locked: bool = True
    ) -> CharacterBible:
        """Extrait la bible canonique des personnages et verrouille chaque fiche."""
        pass
