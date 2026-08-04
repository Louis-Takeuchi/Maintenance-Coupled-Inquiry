from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from constitutive_inquiry.protocol import UNIFIED_OBSERVATION_BUDGET, UNIFIED_SHIFT_OBSERVATION
from constitutive_inquiry.unified_experiment import run_unified_suite


from constitutive_inquiry.confirmation_lock import (
    PROTOCOL_VERSION,
    ConfirmationLocked,
    sha256_file,
    validate_activation,
)


ROOT = Path(__file__).resolve().parent
PRE_RUN_MANIFEST = ROOT / "manifests" / "PRE_RUN_MANIFEST_CANDIDATE_v0_3.json"
ACTIVATION_MANIFEST = ROOT / "manifests" / "CONFIRMATION_ACTIVATION.json"
PRIMARY_PLAN = ROOT / "manifests" / "primary_chunk_plan_v0_3.csv"
ABLATION_PLAN = ROOT / "manifests" / "ablation_chunk_plan_v0_3.csv"
YOKE_MAP = ROOT / "manifests" / "confirmatory_yoke_map_v0_3.csv"


def _load_chunk(chunk_id: str) -> dict[str, str]:
    matches: list[dict[str, str]] = []
    for plan in (PRIMARY_PLAN, ABLATION_PLAN):
        with plan.open(newline="", encoding="utf-8") as handle:
            matches.extend(row for row in csv.DictReader(handle) if row["chunk_id"] == chunk_id)
    if len(matches) != 1:
        raise ValueError(f"chunk_id must match exactly one frozen plan row: {chunk_id}")
    return matches[0]


def _load_yoke_map() -> dict[int, int]:
    with YOKE_MAP.open(newline="", encoding="utf-8") as handle:
        return {int(row["focal_seed"]): int(row["donor_seed"]) for row in csv.DictReader(handle)}


def _parse_csv_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one frozen Paper B confirmatory chunk after explicit activation only."
    )
    parser.add_argument("--chunk-id", required=True, help="Frozen chunk ID such as P000 or A000.")
    parser.add_argument(
        "--output-root",
        default=str(ROOT / "results" / "confirmation" / "v0_3"),
        help="Root directory; each chunk is written once to a new subdirectory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        activation = validate_activation(PRE_RUN_MANIFEST, ACTIVATION_MANIFEST)
    except ConfirmationLocked as exc:
        raise SystemExit(str(exc)) from exc
    chunk = _load_chunk(args.chunk_id)
    seeds = [int(value) for value in _parse_csv_list(chunk["seeds"])]
    if any(seed < 30_000 or seed > 30_071 for seed in seeds):
        raise SystemExit("frozen confirmatory wrapper accepts only seeds 30000–30071")
    conditions = _parse_csv_list(chunk["conditions"])
    relevances = _parse_csv_list(chunk["relevance"])
    common_decoder = bool(int(chunk["common_decoder"]))
    expected_rows = int(chunk["expected_source_rows"])

    output = Path(args.output_root) / args.chunk_id
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing confirmatory chunk: {output}")

    summaries, _ = run_unified_suite(
        output,
        seeds,
        split="confirmation",
        condition_ids=conditions,
        relevance_levels=relevances,
        yoke_map_override=_load_yoke_map(),
        write_traces=True,
        run_common_decoder=common_decoder,
        budget=UNIFIED_OBSERVATION_BUDGET,
        shift=UNIFIED_SHIFT_OBSERVATION,
    )
    if len(summaries) != expected_rows:
        raise RuntimeError(f"chunk row mismatch: expected {expected_rows}, got {len(summaries)}")

    receipt = {
        "protocol_version": PROTOCOL_VERSION,
        "chunk_id": args.chunk_id,
        "activation_manifest_sha256": sha256_file(ACTIVATION_MANIFEST),
        "freeze_candidate_manifest_sha256": activation["freeze_candidate_manifest_sha256"],
        "source_rows": len(summaries),
        "output": str(output),
    }
    with (output / "execution_receipt.json").open("w", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"completed frozen confirmatory chunk {args.chunk_id}: {len(summaries)} source rows")


if __name__ == "__main__":
    main()
