"""Tests unitaires pour l'assemblage vidéo FFmpeg, transitions et normalisation EBU R128."""

import tempfile
from pathlib import Path
from manga_studio.adapters.assembly.ffmpeg_assembler_adapter import FFmpegVideoAssemblerAdapter
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)


def create_segment(ordre: int, duration: float = 6.0) -> StoryboardSegment:
    return StoryboardSegment(
        ordre=ordre,
        scene_id=f"scene_{ordre:03d}",
        titre=f"Scène {ordre}",
        source_refs=[],
        frame="Action",
        characters_present=["ra"],
        reference_character_ids=["ra"],
        audio_script=[AudioScriptItem(speaker="Râ", kind="dialogue", text="Texte")],
        prompt_ia="Action prompt. epic anime style",
        duree_s=duration,
        emotion="épique",
        plan="medium",
        decor="palais",
        continuity_in="",
        continuity_out="",
        transition=TransitionConfig(type="fade", duration_s=0.3)
    )


def test_ffmpeg_command_builder_xfade_and_loudnorm():
    """Vérifie que la commande FFmpeg intègre le cadrage 9:16, xfade et le filtre EBU R128 (-14 LUFS)."""
    assembler = FFmpegVideoAssemblerAdapter()
    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages"),
        target_lufs=-14.0,
        target_true_peak=-1.0,
        transition_duration_s=0.3
    )

    clip_paths = [Path("/tmp/clip1.mp4"), Path("/tmp/clip2.mp4"), Path("/tmp/clip3.mp4")]
    segments = [create_segment(1, 5.0), create_segment(2, 6.0), create_segment(3, 4.0)]
    output_path = Path("/tmp/conte_final.mp4")

    cmd = assembler.build_filter_complex_command(clip_paths, segments, output_path, config)
    cmd_str = " ".join(cmd)

    # Vérifications des paramètres clés
    assert "loudnorm=I=-14.0:TP=-1.0:LRA=11" in cmd_str
    assert "xfade=transition=fade" in cmd_str
    assert "acrossfade=d=0.3" in cmd_str
    assert "1080:1920" in cmd_str
    assert "libx264" in cmd_str
    assert "aac" in cmd_str


def test_ffmpeg_assemble_offline_fixture():
    """Vérifie l'exécution d'assemblage sur des clips fixtures en mode hors-ligne."""
    assembler = FFmpegVideoAssemblerAdapter()
    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages")
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        c1 = tmp_path / "001.mp4"
        c2 = tmp_path / "002.mp4"
        out = tmp_path / "conte_final.mp4"

        c1.write_bytes(b"\x00\x00\x00\x1cftypisom" + b"clip1_data")
        c2.write_bytes(b"\x00\x00\x00\x1cftypisom" + b"clip2_data")

        segments = [create_segment(1, 5.0), create_segment(2, 5.0)]
        res_path = assembler.assemble([c1, c2], segments, out, config)

        assert res_path.exists()
        assert res_path.stat().st_size > 0
        
        probe_info = assembler.inspect_with_ffprobe(res_path)
        assert "status" in probe_info
