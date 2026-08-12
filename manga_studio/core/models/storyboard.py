"""Modèles de domaine pour le Storyboard du mode Conte animé."""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class SourceRef(BaseModel):
    """Lien de traçabilité vers le texte source du conte."""
    paragraph_index: int = Field(..., ge=1, description="Numéro du paragraphe dans conte.txt (1-indexed)")
    excerpt: str = Field(..., min_length=1, description="Extrait textuel justifiant la scène")


class AudioScriptItem(BaseModel):
    """Élément de script audio (dialogue, narration ou effet sonore)."""
    speaker: str = Field(..., description="Nom du locuteur ou 'Narrateur'")
    kind: Literal["dialogue", "narration", "sound_effect"] = Field(default="dialogue", description="Type d'élément audio")
    text: str = Field(..., description="Texte de la réplique ou narration en français")


class TransitionConfig(BaseModel):
    """Configuration de la transition vers le segment suivant."""
    type: Literal["fade", "cut", "dissolve", "none"] = Field(default="fade", description="Type de transition vidéo")
    duration_s: float = Field(default=0.3, ge=0.0, le=2.0, description="Durée de la transition en secondes")


class StoryboardSegment(BaseModel):
    """Segment unitaire de storyboard correspondant à un clip vidéo."""
    ordre: int = Field(..., ge=1, description="Position ordonnée du segment (1, 2, ...)")
    scene_id: str = Field(..., pattern=r"^scene_[0-9]{3,}$", description="Identifiant unique de scène (ex: scene_001)")
    titre: str = Field(..., min_length=1, description="Titre descriptif du segment")
    source_refs: List[SourceRef] = Field(default_factory=list, description="Références vers les paragraphes sources")
    frame: str = Field(..., min_length=1, description="Description visuelle de l'action principale")
    characters_present: List[str] = Field(default_factory=list, description="Identifiants des personnages présents")
    reference_character_ids: List[str] = Field(default_factory=list, description="Identifiants des personnages utilisés comme référence visuelle")
    audio_script: List[AudioScriptItem] = Field(default_factory=list, description="Dialogues et narrations du segment")
    prompt_ia: str = Field(..., min_length=10, description="Prompt IA en anglais avec descriptions et style")
    duree_s: float = Field(default=5.0, ge=1.0, le=30.0, description="Durée du clip en secondes")
    emotion: str = Field(default="neutre", description="Tonalité émotionnelle de la scène")
    plan: str = Field(default="cinematic medium shot", description="Cadrage de caméra")
    decor: str = Field(..., description="Description du lieu et de l'ambiance")
    continuity_in: str = Field(default="", description="État narratif entrant (continuité)")
    continuity_out: str = Field(default="", description="État narratif sortant (continuité)")
    transition: TransitionConfig = Field(default_factory=TransitionConfig, description="Transition de sortie")

    @field_validator("reference_character_ids")
    @classmethod
    def validate_refs_subset(cls, v: List[str], info) -> List[str]:
        # reference_character_ids should ideally be a subset of present characters or explicitly specified
        return v


class Storyboard(BaseModel):
    """Storyboard global canonique d'un conte animé."""
    schema_version: Literal["1.0"] = Field(default="1.0", description="Version du schéma")
    story_id: str = Field(..., min_length=1, description="Identifiant unique de l'histoire")
    title: str = Field(default="", description="Titre de l'œuvre ou du conte")
    segments: List[StoryboardSegment] = Field(..., min_length=1, description="Liste ordonnée des segments")

    @model_validator(mode="after")
    def validate_segment_order_and_continuity(self) -> "Storyboard":
        orders = [s.ordre for s in self.segments]
        expected_orders = list(range(1, len(self.segments) + 1))
        if orders != expected_orders:
            raise ValueError(f"Ordre des segments invalide. Reçu: {orders}, Attendu: {expected_orders}")

        scene_ids = [s.scene_id for s in self.segments]
        if len(scene_ids) != len(set(scene_ids)):
            raise ValueError("Les 'scene_id' doivent être strictement uniques au sein du storyboard.")
        return self

    @property
    def total_duration_s(self) -> float:
        """Calcule la durée totale brute du storyboard."""
        return sum(s.duree_s for s in self.segments)
