"""Générateur de fichiers de sous-titres synchronisés SRT et ASS."""

from typing import List, Tuple
from manga_studio.core.models.storyboard import StoryboardSegment


class SubtitleGenerator:
    """Génère les sous-titres synchronisés à partir des segments du storyboard."""

    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _format_ass_time(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int(round((seconds - int(seconds)) * 100))
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{centis:02d}"

    @classmethod
    def generate_srt(cls, segments: List[StoryboardSegment]) -> str:
        """Génère le texte complet du sous-titre au format SubRip (.srt)."""
        entries = []
        current_time = 0.0
        subtitle_index = 1

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
                    speaker_prefix = f"[{item.speaker}] " if item.speaker and item.speaker.lower() != "narrateur" else ""
                    text_line = f"{speaker_prefix}{item.text}"

                    entry = (
                        f"{subtitle_index}\n"
                        f"{cls._format_srt_time(t_start)} --> {cls._format_srt_time(t_end)}\n"
                        f"{text_line}\n"
                    )
                    entries.append(entry)
                    subtitle_index += 1

            current_time = seg_end

        return "\n".join(entries)

    @classmethod
    def generate_ass(cls, segments: List[StoryboardSegment], title: str = "Conte Animé") -> str:
        """Génère le texte complet du sous-titre au format Advanced SubStation Alpha (.ass)."""
        header = f"""[Script Info]
Title: {title}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,40,40,120,1

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
                    speaker_prefix = f"\\b1[{item.speaker}]\\b0 " if item.speaker and item.speaker.lower() != "narrateur" else ""
                    text_line = f"{speaker_prefix}{item.text}"

                    line = f"Dialogue: 0,{cls._format_ass_time(t_start)},{cls._format_ass_time(t_end)},Default,,0,0,0,,{text_line}"
                    dialogues.append(line)

            current_time = seg_end

        return header + "\n".join(dialogues) + "\n"
