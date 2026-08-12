"""Tests unitaires pour les adaptateurs de synchronisation labiale (LipSync)."""

import tempfile
from pathlib import Path
import pytest
from manga_studio.adapters.lipsync.mock_lipsync_adapter import MockLipSyncAdapter
from manga_studio.adapters.lipsync.wav2lip_adapter import Wav2LipAdapter


def test_mock_lipsync_adapter_execution():
    """Vérifie le fonctionnement nominal de l'adaptateur Mock LipSync."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        vid_in = tmp_path / "in.mp4"
        aud_in = tmp_path / "voice.wav"
        out = tmp_path / "lipsync_out.mp4"

        vid_in.write_bytes(b"\x00" * 100)
        aud_in.write_bytes(b"\x00" * 100)

        adapter = MockLipSyncAdapter()
        res = adapter.apply_lipsync(vid_in, aud_in, out)
        assert res.exists()
        assert res.stat().st_size > 0


def test_wav2lip_adapter_missing_files_error():
    """Vérifie que des fichiers inexistants lèvent FileNotFoundError."""
    adapter = Wav2LipAdapter()
    with pytest.raises(FileNotFoundError):
        adapter.apply_lipsync(Path("/tmp/non_existent.mp4"), Path("/tmp/non_existent.wav"), Path("/tmp/out.mp4"))


def test_wav2lip_adapter_execution_success():
    """Vérifie l'exécution avec gestion mémoire GPU sur fichiers existants."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        vid_in = tmp_path / "in.mp4"
        aud_in = tmp_path / "voice.wav"
        out = tmp_path / "lipsync_out.mp4"

        vid_in.write_bytes(b"\x00" * 256)
        aud_in.write_bytes(b"\x00" * 256)

        adapter = Wav2LipAdapter()
        res = adapter.apply_lipsync(vid_in, aud_in, out, face_crop_box=(100, 100, 300, 300))
        assert res.exists()
        assert res.stat().st_size > 0
