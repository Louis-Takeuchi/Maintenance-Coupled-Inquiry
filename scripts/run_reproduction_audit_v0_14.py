from __future__ import annotations

import csv
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from constitutive_inquiry.agent import MODES

AUDIT_MODES = (
    "confidence_gated_relational_generation",
    "sparse_reset_generation",
    "quarantine_no_local_reservation_generation",
    "no_null_confidence_gated_generation",
)

RESULTS = ROOT / "results"
TRAINING_MEMORY = RESULTS / "training" / "relational_memory.json"
OUT = RESULTS / "reproduction"
SEED_START = 18100
SEED_END = 18101
BUDGET = 280
SHIFT = 28


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return sorted(rows, key=lambda row: (int(row["seed"]), row["relevance"], row["mode"]))


def run_audit(target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    for mode in AUDIT_MODES:
        command = [
            sys.executable,
            str(ROOT / "run_mode_v0_14.py"),
            "--mode", mode,
            "--seed-start", str(SEED_START),
            "--seed-end", str(SEED_END),
            "--output", str(target),
            "--relational-memory", str(TRAINING_MEMORY),
            "--budget", str(BUDGET),
            "--shift", str(SHIFT),
            "--split", "reproduction",
        ]
        subprocess.run(command, cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL)

    combined = target / "audit.csv"
    all_rows: list[dict[str, str]] = []
    fieldnames: list[str] | None = None
    for mode in AUDIT_MODES:
        source = target / f"{mode}_run_summaries.csv"
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if fieldnames is None:
                fieldnames = list(reader.fieldnames or [])
            all_rows.extend(reader)

    all_rows.sort(key=lambda row: (int(row["seed"]), row["relevance"], row["mode"]))
    if not fieldnames:
        raise RuntimeError("No reproduction rows were produced")
    with combined.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    return combined


def main() -> None:
    if not TRAINING_MEMORY.exists():
        raise FileNotFoundError(f"Missing frozen training memory: {TRAINING_MEMORY}")
    if OUT.exists():
        shutil.rmtree(OUT)

    run_a = run_audit(OUT / "run_a")
    run_b = run_audit(OUT / "run_b")
    rows_a = normalized(run_a)
    rows_b = normalized(run_b)
    rows_equal = rows_a == rows_b
    bytes_equal = run_a.read_bytes() == run_b.read_bytes()
    expected_rows = (SEED_END - SEED_START) * 2 * len(AUDIT_MODES)

    report_lines = [
        "Constitutive Inquiry MVP v0.14 reproduction audit",
        f"seed_range={SEED_START}-{SEED_END - 1}",
        f"modes={len(AUDIT_MODES)}",
        "relevance_classes=2",
        f"expected_rows_per_run={expected_rows}",
        f"rows_a={len(rows_a)}",
        f"rows_b={len(rows_b)}",
        f"normalized_rows_equal={rows_equal}",
        f"csv_bytes_equal={bytes_equal}",
        f"sha256_a={sha256(run_a)}",
        f"sha256_b={sha256(run_b)}",
        "status=PASS" if rows_equal and bytes_equal and len(rows_a) == expected_rows else "status=FAIL",
    ]
    report = OUT / "reproduction_audit_v0_14.txt"
    report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print("\n".join(report_lines))
    if not (rows_equal and bytes_equal and len(rows_a) == expected_rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
