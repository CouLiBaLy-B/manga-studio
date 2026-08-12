"""Modèles de domaine pour les fiches personnages et bibles de personnages."""

from typing import List
from pydantic import BaseModel, Field, field_validator


class PhysicalDescription(BaseModel):
    """Description physique canonique du personnage."""
    silhouette: str = Field(..., description="Silhouette générale (ex: grande silhouette royale)")
    visage: str = Field(..., description="Traits du visage et regard (ex: traits adultes, regard calme)")
    peau: str = Field(..., description="Couleur/teinte de peau (ex: brun chaud)")
    coiffure: str = Field(..., description="Coiffure ou couvre-chef (ex: coiffe royale dorée)")
    tenue: str = Field(..., description="Vêtements principaux (ex: robe blanche et or)")
    couleurs_hex: List[str] = Field(default_factory=list, description="Codes hexadécimaux des couleurs clés")
    accessoires_signature: List[str] = Field(default_factory=list, description="Accessoires ou armes distinctifs")

    @field_validator("couleurs_hex")
    @classmethod
    def validate_hex(cls, v: List[str]) -> List[str]:
        for code in v:
            if not code.startswith("#") or len(code) not in (4, 7):
                raise ValueError(f"Code hexadécimal invalide: {code}")
        return v


class SuggestedVoice(BaseModel):
    """Suggestions pour la voix et l'interprétation audio."""
    langue: str = Field(default="français", description="Langue de synthèse")
    ton: str = Field(..., description="Ton de la voix (ex: grave, posé, bienveillant)")


class CharacterSheet(BaseModel):
    """Fiche personnage canonique et verrouillée."""
    character_id: str = Field(..., description="Identifiant unique (ex: ra, gardien_01)")
    nom: str = Field(..., description="Nom complet ou usuel du personnage")
    role: str = Field(..., description="Rôle narratif (ex: dieu solaire, personnage principal)")
    source_image_ids: List[str] = Field(..., min_length=1, description="Fichiers images de référence source")
    description_physique: PhysicalDescription = Field(..., description="Attributs physiques invariables")
    traits_caractere: List[str] = Field(default_factory=list, description="Traits psychologiques")
    voix_suggeree: SuggestedVoice = Field(..., description="Spécifications vocales")
    style_constraints: List[str] = Field(
        default_factory=lambda: ["epic anime style", "consistent character design", "no text artifacts"],
        description="Contraintes de rendu visuel"
    )
    locked: bool = Field(default=True, description="Indicateur d'immuabilité (doit rester True)")

    @field_validator("locked")
    @classmethod
    def validate_locked(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Une fiche personnage canonique doit obligatoirement être verrouillée (locked=True)")
        return v


class CharacterBible(BaseModel):
    """Bible complète des personnages d'un conte."""
    story_id: str = Field(..., description="Identifiant unique du conte")
    characters: List[CharacterSheet] = Field(..., min_length=1, description="Liste des fiches personnages")
    version: str = Field(default="1.0", description="Version de la bible")
    locked: bool = Field(default=True, description="Verrou global de la bible")

    def get_character(self, character_id: str) -> CharacterSheet:
        for char in self.characters:
            if char.character_id == character_id:
                return char
        raise KeyError(f"Personnage introuvable dans la bible: '{character_id}'")
