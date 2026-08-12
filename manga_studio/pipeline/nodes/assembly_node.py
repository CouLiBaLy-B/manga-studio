"""Nœud 6 : Assemblage vidéo déterministe, normalisation sonore EBU R128 et sous-titrage."""

import uuid
from pathlib import Path
from typing import Dict, List
from manga_studio.core.models.manifest import ManifestEvent
from manga_studio.core.ports.artifact_store import ArtifactStorePort
from manga_studio.core.ports.video_assembler import VideoAssemblerPort
from manga_studio.core.subtitle_generator import SubtitleGenerator
from manga_studio.pipeline.state import TalePipelineState


class AssemblyNode:
    """Génère les sous-titres et assemble la vidéo verticale finale via FFmpeg."""

    def __init__(
        self,
        video_assembler: VideoAssemblerPort,
        artifact_store: ArtifactStorePort
    ):
        self.video_assembler = video_assembler
        self.artifact_store = artifact_store

    def execute(self, state: TalePipelineState) -> TalePipelineState:
        storyboard = state["validated_storyboard"]
        clip_paths_map = state["clip_paths"]
        config = state["config"]

        # 1. Génération des sous-titres SRT et ASS
        subtitles_paths: Dict[str, Path] = {}
        if config.generate_subtitles:
            srt_content = SubtitleGenerator.generate_srt(storyboard.segments)
            ass_content = SubtitleGenerator.generate_ass(storyboard.segments, title=storyboard.title or state["story_id"])

            srt_path = self.artifact_store.root_dir / "subtitles" / "conte.srt"
            ass_path = self.artifact_store.root_dir / "subtitles" / "conte.ass"

            srt_path.write_text(srt_content, encoding="utf-8")
            ass_path.write_text(ass_content, encoding="utf-8")

            subtitles_paths["srt"] = srt_path
            subtitles_paths["ass"] = ass_path

        # 2. Ordonnancement rigoureux des clips
        ordered_clip_paths: List[Path] = []
        for seg in storyboard.segments:
            p = clip_paths_map.get(seg.scene_id)
            if p and p.exists():
                ordered_clip_paths.append(p)
            else:
                raise FileNotFoundError(f"Clip manquant pour la scène : {seg.scene_id}")

        # 3. Assemblage vidéo final
        final_video_target = self.artifact_store.root_dir / "conte_final.mp4"
        assembled_video = self.video_assembler.assemble(
            clip_paths=ordered_clip_paths,
            segments=storyboard.segments,
            output_video_path=final_video_target,
            config=config,
            subtitles_path=subtitles_paths.get("ass") or subtitles_paths.get("srt")
        )

        # 4. Journalisation manifest
        self.artifact_store.append_manifest_event(
            ManifestEvent(
                event_id=str(uuid.uuid4()),
                step="assembly",
                action="assemble_final_video",
                status="SUCCESS",
                details={
                    "total_clips_assembled": len(ordered_clip_paths),
                    "target_resolution": config.target_resolution,
                    "target_lufs": config.target_lufs,
                    "target_true_peak": config.target_true_peak,
                    "final_video_path": str(assembled_video),
                    "final_video_sha256": self.artifact_store.compute_sha256(assembled_video),
                    "subtitles_generated": list(subtitles_paths.keys())
                }
            )
        )

        state["subtitles_paths"] = subtitles_paths
        state["final_video_path"] = assembled_video
        return state
