"""Tests unitaires pour l'interface CLI de MangaTok Studio."""

import tempfile
from pathlib import Path
from manga_studio.cli.main import main


def test_cli_execution_help(capsys):
    """Vérifie l'aide CLI."""
    try:
        main(["--help"])
    except SystemExit as e:
        assert e.code == 0


def test_cli_nominal_execution():
    """Vérifie l'exécution réussie de la CLI sur la fixture de conte."""
    with tempfile.TemporaryDirectory() as tmp_output:
        args = [
            "--story", "tests/fixtures/conte.txt",
            "--characters-dir", "tests/fixtures/personnages",
            "--output-dir", tmp_output,
            "--profile", "research",
            "--territory", "EU",
            "--use-mock-video"
        ]
        ret = main(args)
        assert ret == 0
        assert (Path(tmp_output) / "conte_final.mp4").exists()
