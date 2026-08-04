#!/usr/bin/env python3
"""Compare regenerated CSV rows with the frozen released analysis tables."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data/analysis/v0_3_final_analysis"
FILES = [
    "primary_endpoint_intervals.csv",
    "primary_condition_summary.csv",
    "common_decoder_diagnostics.csv",
    "ablation_condition_summary.csv",
    "ablation_paired_diagnostics.csv",
]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    candidate = Path(sys.argv[1]) if len(sys.argv) == 2 else ROOT / "build/reproduced-analysis"
    for filename in FILES:
        expected_path = CANONICAL / filename
        actual_path = candidate / filename
        if not actual_path.exists():
            raise SystemExit(f"FAIL missing reproduced file: {actual_path}")
        expected = rows(expected_path)
        actual = rows(actual_path)
        if expected != actual:
            raise SystemExit(f"FAIL row mismatch: {filename}")
        print(f"PASS {filename}: {len(actual)} rows")
    print("PASS reproduced analysis matches frozen released tables")


if __name__ == "__main__":
    main()

