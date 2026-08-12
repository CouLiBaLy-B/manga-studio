"""Port pour la génération du Storyboard via LLM distant ou local."""

from abc import ABC, abstractmethod
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import Storyboard


class StoryboardLLMPort(ABC):
    """Interface pour les générateurs de Storyboard LLM."""

    @abstractmethod
    def generate_storyboard(
        self,
        story_id: str,
        tale_text: str,
        character_bible: CharacterBible,
        config: TalePipelineConfig
    ) -> Storyboard:
        """Génère un storyboard complet et structuré validé par Pydantic."""
        pass
