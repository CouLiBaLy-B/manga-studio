"""Générateur de métadonnées et accroches pour réseaux sociaux (TikTok, Reels, Shorts)."""

import re
from typing import Dict, List
from pydantic import BaseModel, Field
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.storyboard import Storyboard


class TikTokMetadata(BaseModel):
    """Métadonnées optimisées pour l'algorithme TikTok."""
    hook_phrase: str = Field(..., description="Accroche des 3 premières secondes")
    viral_title: str = Field(..., description="Titre percutant")
    caption: str = Field(..., description="Légende courte (max 150 car.)")
    hashtags: List[str] = Field(default_factory=list)
    suggested_sound: str = Field(default="Epic Anime Myth Theme")


class YouTubeShortsMetadata(BaseModel):
    """Métadonnées SEO pour YouTube Shorts."""
    title: str = Field(..., description="Titre YouTube avec mot-clé")
    description: str = Field(..., description="Description complète avec timecodes")
    tags: List[str] = Field(default_factory=list)


class SocialPackage(BaseModel):
    """Package complet multi-plateformes de diffusion."""
    story_id: str
    tiktok: TikTokMetadata
    youtube_shorts: YouTubeShortsMetadata
    instagram_reels_caption: str


class SocialMetadataGenerator:
    """Génère les packages de publication sociale à partir du storyboard et des personnages."""

    @classmethod
    def generate_package(
        cls,
        story_id: str,
        storyboard: Storyboard,
        character_bible: CharacterBible
    ) -> SocialPackage:
        """Produit des accroches, descriptions et hashtags viraux adaptés."""
        main_char = character_bible.characters[0].nom if character_bible.characters else "Le Héros"
        first_scene = storyboard.segments[0] if storyboard.segments else None

        hook = f"Ce que {main_char} a découvert va changer le destin de l'Égypte... ☀️"
        if first_scene and first_scene.audio_script:
            hook = f"« {first_scene.audio_script[0].text[:60]}... »"

        title_tt = f"L'Incroyable Légende de {main_char} ⚡ #MangaTok"
        caption_tt = f"Plongez dans le mythe de {main_char} ! Qui aurait osé défier les dieux ? 👀 Dis-nous en commentaire !"
        tags_tt = ["#manga", "#anime", "#conte", "#tiktokfrance", f"#{main_char.lower().replace(' ', '')}", "#histoire"]

        # YouTube Shorts
        title_yt = f"L'Épopée Sacrée de {main_char} | Conte Animé Manga [Shorts]"
        desc_yt = (
            f"Découvrez l'histoire animée de {main_char}.\n\n"
            f"🎬 Réalisé avec MangaTok Studio\n"
            f"⏱️ Durée : {storyboard.total_duration_s:.1f}s\n"
            f"📌 Chapitres :\n"
        )
        cumul_t = 0.0
        for seg in storyboard.segments:
            desc_yt += f"- {int(cumul_t)}s : {seg.titre}\n"
            cumul_t += seg.duree_s

        desc_yt += "\n#Shorts #Manga #Animation #Mythologie"
        tags_yt = ["manga", "anime", "histoire", "conte", "animation 3d", "short", main_char.lower()]

        # Instagram
        insta_cap = (
            f"✨ Le Mythe de {main_char} prend vie en animation !\n\n"
            f"Découvrez cette légende millénaire adaptée en format manga.\n\n"
            f"Partage avec un fan de mythologie ! 📲\n\n"
            f"{' '.join(tags_tt[:5])}"
        )

        return SocialPackage(
            story_id=story_id,
            tiktok=TikTokMetadata(
                hook_phrase=hook,
                viral_title=title_tt,
                caption=caption_tt,
                hashtags=tags_tt,
                suggested_sound="Épopée Divine — Manga Studio OST"
            ),
            youtube_shorts=YouTubeShortsMetadata(
                title=title_yt,
                description=desc_yt,
                tags=tags_yt
            ),
            instagram_reels_caption=insta_cap
        )
