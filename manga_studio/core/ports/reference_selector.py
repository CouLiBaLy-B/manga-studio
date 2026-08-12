"""Port pour la sélection et l'ordonnancement déterministe des images de référence."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.storyboard import StoryboardSegment


class ReferenceSelectorPort(ABC):
    """Interface pour la sélection déterministe des images de référence."""

    @abstractmethod
    def select_references_for_segment(
        self,
        segment: StoryboardSegment,
        character_bible: CharacterBible,
        image_store_map: Dict[str, Path],
        max_references: int = 9
    ) -> List[Path]:
        """Retourne la liste ordonnée et déterministe des chemins d'images de référence."""
        pass
