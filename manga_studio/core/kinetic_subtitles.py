"""Générateur de sous-titres cinétiques verticaux au format TikTok/Reels (ASS enrichi)."""

import re
from typing import List
from manga_studio.core.models.storyboard import StoryboardSegment


class KineticSubtitleGenerator:
    """Génère des sous-titres animés avec mise en valeur colorée des mots clés."""

    HIGHLIGHT_COLOR = "&H0042C5F4&"  # Couleur d'accentuation or/jaune
    DEFAULT_COLOR = "&H00FFFFFF&"    # Blanc pur
    OUTLINE_COLOR = "&H00000000&"    # Noir contour

    KEYWORDS_TO_HIGHLIGHT = {
        "soleil", "lumière", "barque", "dieu", "râ", "gardien", "sacrée", "destin", "étoile",
        "ciel", "nuit", "nil", "éternel", "puissant", "magie", "pharaon", "royaume"
    }

    @classmethod
    def generate_kinetic_ass(cls, segments: List[StoryboardSegment], title: str = "Conte Animé") -> str:
        """Génère un script ASS avec typographie dynamique et mise en relief."""
        header = f"""[Script Info]
Title: {title} - Kinetic TikTok Edition
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticMain,Arial Black,58,{cls.DEFAULT_COLOR},&H000000FF,{cls.OUTLINE_COLOR},&H90000000,-1,0,0,0,100,100,2,0,1,5,2,2,60,60,320,1
Style: SpeakerTag,Arial,40,{cls.HIGHLIGHT_COLOR},&H000000FF,{cls.OUTLINE_COLOR},&H90000000,-1,0,0,0,100,100,1,0,1,3,1,2,60,60,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        dialogues = []
        current_time = 0.0

        for seg in segments:
            seg_start = current_time
            seg_duration = seg.duree_s
            seg_end = seg_start + seg_duration

            if seg.audio_script:
                num_items = len(seg.audio_script)
                item_duration = seg_duration / num_items

                for i, item in enumerate(seg.audio_script):
                    t_start = seg_start + (i * item_duration)
                    t_end = t_start + item_duration

                    t_start_fmt = cls._format_ass_time(t_start)
                    t_end_fmt = cls._format_ass_time(t_end)

                    # 1. Étiquette de locuteur
                    if item.speaker and item.speaker.lower() != "narrateur":
                        speaker_line = (
                            f"Dialogue: 1,{t_start_fmt},{t_end_fmt},SpeakerTag,,0,0,0,,{{\\fad(150,150)}}☀️ {item.speaker.upper()}"
                        )
                        dialogues.append(speaker_line)

                    # 2. Texte avec mots-clés rehaussés en couleur
                    styled_text = cls._highlight_keywords(item.text)
                    anim_effect = "{\\fad(100,100)\\t(0,120,\\fscx106\\fscy106)\\t(120,240,\\fscx100\\fscy100)}"
                    dialogue_line = f"Dialogue: 0,{t_start_fmt},{t_end_fmt},KineticMain,,0,0,0,,{anim_effect}{styled_text}"
                    dialogues.append(dialogue_line)

            current_time = seg_end

        return header + "\n".join(dialogues) + "\n"

    @classmethod
    def _highlight_keywords(cls, text: str) -> str:
        """Entoure les mots clés de balises de couleur ASS."""
        words = text.split(" ")
        styled_words = []
        for w in words:
            clean_w = re.sub(r"[^\w]", "", w).lower()
            if clean_w in cls.KEYWORDS_TO_HIGHLIGHT:
                styled_words.append(f"{{\\c{cls.HIGHLIGHT_COLOR}}}{w}{{\\c{cls.DEFAULT_COLOR}}}")
            else:
                styled_words.append(w)
        return " ".join(styled_words)

    @staticmethod
    def _format_ass_time(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int(round((seconds - int(seconds)) * 100))
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{centis:02d}"
