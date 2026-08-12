"""Tests unitaires pour les Fiches Personnages et la règle d'immuabilité (locked=True)."""

import pytest
from pydantic import ValidationError
from manga_studio.core.models.character import (
    CharacterBible,
    CharacterSheet,
    PhysicalDescription,
    SuggestedVoice,
)


def test_character_sheet_valid_creation():
    """Vérifie la création valide d'une fiche personnage canonique conforme."""
    phys = PhysicalDescription(
        silhouette="grande silhouette royale",
        visage="traits adultes, regard calme",
        peau="brun chaud",
        coiffure="coiffe royale dorée",
        tenue="robe blanche et or",
        couleurs_hex=["#F4C542", "#F7F2E8", "#8A5A2B"],
        accessoires_signature=["disque solaire", "sceptre"]
    )
    voice = SuggestedVoice(langue="français", ton="grave, posé, bienveillant")
    sheet = CharacterSheet(
        character_id="ra",
        nom="Râ",
        role="dieu solaire, personnage principal",
        source_image_ids=["personnage_01.png"],
        description_physique=phys,
        traits_caractere=["solennel", "protecteur", "sage"],
        voix_suggeree=voice,
        style_constraints=["epic anime style", "consistent character design", "no text artifacts"],
        locked=True
    )
    assert sheet.character_id == "ra"
    assert sheet.locked is True
    assert "#F4C542" in sheet.description_physique.couleurs_hex


def test_character_sheet_locked_immutable():
    """Vérifie qu'une fiche avec locked=False est strictement rejetée."""
    phys = PhysicalDescription(
        silhouette="silhouette",
        visage="visage",
        peau="peau",
        coiffure="coiffe",
        tenue="tenue",
        couleurs_hex=["#FFFFFF"],
        accessoires_signature=[]
    )
    voice = SuggestedVoice(langue="français", ton="posé")
    
    with pytest.raises(ValidationError):
        CharacterSheet(
            character_id="test_unlocked",
            nom="Test",
            role="role",
            source_image_ids=["img.png"],
            description_physique=phys,
            traits_caractere=[],
            voix_suggeree=voice,
            locked=False  # Doit lever une erreur
        )


def test_character_sheet_hex_color_validation():
    """Vérifie le rejet des codes hexadécimaux invalides."""
    with pytest.raises(ValidationError):
        PhysicalDescription(
            silhouette="s",
            visage="v",
            peau="p",
            coiffure="c",
            tenue="t",
            couleurs_hex=["invalid_hex_color"],
            accessoires_signature=[]
        )


def test_character_bible_lookup():
    """Vérifie la recherche de personnages par identifiant dans la bible."""
    phys = PhysicalDescription(
        silhouette="s",
        visage="v",
        peau="p",
        coiffure="c",
        tenue="t",
        couleurs_hex=["#000000"],
        accessoires_signature=[]
    )
    sheet = CharacterSheet(
        character_id="gardien_01",
        nom="Gardien",
        role="sentinelle",
        source_image_ids=["gardien.png"],
        description_physique=phys,
        traits_caractere=[],
        voix_suggeree=SuggestedVoice(ton="ferme"),
        locked=True
    )
    bible = CharacterBible(story_id="mythe", characters=[sheet], locked=True)
    found = bible.get_character("gardien_01")
    assert found.nom == "Gardien"

    with pytest.raises(KeyError):
        bible.get_character("inconnu")
