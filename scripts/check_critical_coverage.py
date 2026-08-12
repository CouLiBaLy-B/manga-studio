#!/usr/bin/env python3
"""Vérifie des seuils de couverture ciblés pour les modules critiques."""

from __future__ import annotations

import json
import sys
from pathlib import Path

THRESHOLDS = {
    "manga_studio/api/app.py": 60.0,
    "manga_studio/jobs.py": 70.0,
    "manga_studio/pipeline/graph.py": 90.0,
}


def main() -> int:
    report_path = Path(sys.argv[1] if len(sys.argv) > 1 else "coverage.json")
    if not report_path.exists():
        print(f"Rapport de couverture absent : {report_path}", file=sys.stderr)
        return 2
    report = json.loads(report_path.read_text(encoding="utf-8"))
    files = report.get("files", {})
    failures = []
    for module, minimum in THRESHOLDS.items():
        coverage = files.get(module, {}).get("summary", {}).get("percent_covered")
        if coverage is None or coverage < minimum:
            failures.append(f"{module}: {coverage if coverage is not None else 'absent'} % (minimum {minimum} %)")
        else:
            print(f"OK {module}: {coverage:.2f} % (minimum {minimum:.2f} %)")
    if failures:
        print("Échec des seuils ciblés :", *failures, sep="\n", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
