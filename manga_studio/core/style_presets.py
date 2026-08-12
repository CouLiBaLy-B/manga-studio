"""Bibliothèque et registre des Presets Stylistiques Manga & Animation."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StylePreset(BaseModel):
    """Définition d'un preset stylistique pour la cohérence de rendu IA."""
    key: str = Field(..., description="Identifiant unique du style (ex: shonen_epic)")
    name: str = Field(..., description="Nom d'affichage du style")
    description: str = Field(..., description="Description artistique")
    prompt_suffix: str = Field(..., description="Suffixe descriptif injecté dans les prompts")
    negative_prompt: str = Field(
        default="blurry, distorted, text, watermark, bad anatomy, low quality, artifacts",
        description="Prompt négatif standard"
    )
    recommended_framing: str = Field(default="cinematic dynamic shot")
    lora_trigger_words: List[str] = Field(default_factory=list)


class StylePresetRegistry:
    """Catalogue des styles graphiques manga intégrés."""

    _PRESETS: Dict[str, StylePreset] = {
        "shonen_epic": StylePreset(
            key="shonen_epic",
            name="Shōnen Épique",
            description="Lignes de vitesse dynamiques, contrastes marqués et étincelles énergétiques.",
            prompt_suffix="epic shonen anime style, dynamic composition, sharp lineart, high contrast, vivid colors, masterpiece, no text artifacts",
            recommended_framing="cinematic low angle, dramatic lighting",
            lora_trigger_words=["shonen_style", "action_anime"]
        ),
        "seinen_dark_fantasy": StylePreset(
            key="seinen_dark_fantasy",
            name="Seinen Dark Fantasy",
            description="Ambiance sombre, clair-obscur prononcé, textures réalistes et atmosphère pesante.",
            prompt_suffix="dark fantasy seinen manga style, atmospheric chiaroscuro, gritty detailed textures, cinematic realism, dramatic shadows, no text artifacts",
            recommended_framing="cinematic medium close-up, volumetric lighting",
            lora_trigger_words=["seinen_dark", "grim_fantasy"]
        ),
        "ghibli_poetic": StylePreset(
            key="ghibli_poetic",
            name="Ghibli Poétique",
            description="Aquarelle douce, décors naturels luxuriants et esthétique peinte à la main.",
            prompt_suffix="poetic hand-painted anime aesthetic, lush watercolor backgrounds, soft warm sunlight, charming character design, Studio Ghibli inspired, no text artifacts",
            recommended_framing="scenic wide shot, gentle sunlight",
            lora_trigger_words=["ghibli_art", "watercolor_anime"]
        ),
        "cyberpunk_neo_tokyo": StylePreset(
            key="cyberpunk_neo_tokyo",
            name="Cyberpunk Néo-Tokyo",
            description="Néons vibrants, reflets sur asphalte humide et esthétique futuriste.",
            prompt_suffix="cyberpunk retro-futuristic manga, vibrant neon reflections, atmospheric rain, holographic glows, cinematic anime lighting, no text artifacts",
            recommended_framing="cinematic low angle, anamorphic glow",
            lora_trigger_words=["cyberpunk_manga", "neon_glow"]
        ),
        "watercolor_mythology": StylePreset(
            key="watercolor_mythology",
            name="Mythologie & Or Sacré",
            description="Inspiration enluminures orientales et sumi-e avec touches d'or divines.",
            prompt_suffix="mythological divine anime style, sumi-e ink wash elegance, subtle golden leaf accents, ethereal atmosphere, majestic character presence, no text artifacts",
            recommended_framing="cinematic majestic shot, golden hour glow",
            lora_trigger_words=["mythic_gold", "ancient_divine"]
        )
    }

    @classmethod
    def get_preset(cls, key: str) -> StylePreset:
        """Récupère un preset par sa clé ou renvoie le style par défaut."""
        if key in cls._PRESETS:
            return cls._PRESETS[key]
        return cls._PRESETS["watercolor_mythology"]

    @classmethod
    def list_presets(cls) -> Dict[str, StylePreset]:
        """Retourne l'ensemble des presets disponibles."""
        return dict(cls._PRESETS)
