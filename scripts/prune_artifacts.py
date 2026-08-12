#!/usr/bin/env python3
"""Supprime avec garde-fous les runs d'artefacts expirés.

Le script est non destructif par défaut. Utiliser --confirm est obligatoire pour
supprimer réellement des répertoires de runs.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purger les artefacts MangaTok Studio expirés.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(os.getenv("MANGA_STUDIO_OUTPUT_ROOT", "output")),
        help="Répertoire contenant les runs (défaut : MANGA_STUDIO_OUTPUT_ROOT ou output).",
    )
    parser.add_argument("--older-than-days", type=int, default=30, help="Âge minimal des runs à purger.")
    parser.add_argument("--confirm", action="store_true", help="Autorise réellement les suppressions.")
    return parser.parse_args()


def expired_runs(output_root: Path, older_than_days: int) -> list[Path]:
    if older_than_days < 1:
        raise ValueError("--older-than-days doit être supérieur ou égal à 1.")
    if not output_root.exists():
        return []
    if not output_root.is_dir():
        raise ValueError("--output-root doit être un répertoire.")

    root = output_root.resolve()
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    candidates: list[Path] = []
    for child in root.iterdir():
        if not child.is_dir() or child.is_symlink():
            continue
        # Défense en profondeur : aucune suppression hors de la racine demandée.
        if not child.resolve().is_relative_to(root):
            continue
        modified = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
        if modified < cutoff:
            candidates.append(child)
    return candidates


def main() -> int:
    args = parse_args()
    try:
        candidates = expired_runs(args.output_root, args.older_than_days)
    except ValueError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2

    mode = "SUPPRESSION" if args.confirm else "SIMULATION"
    print(f"{mode} — {len(candidates)} run(s) expiré(s) dans {args.output_root}")
    for run_dir in candidates:
        print(run_dir)
        if args.confirm:
            shutil.rmtree(run_dir)
    if not args.confirm and candidates:
        print("Aucune suppression effectuée. Ajoutez --confirm après vérification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
