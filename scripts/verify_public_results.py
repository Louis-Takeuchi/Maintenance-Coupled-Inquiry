#!/usr/bin/env python3
"""Read-only consistency checks for the published confirmatory summaries."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise SystemExit(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"PASS {label}: {actual}")


def require_close(label: str, actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=5e-13):
        raise SystemExit(f"FAIL {label}: expected {expected}, got {actual}")
    print(f"PASS {label}: {actual:.10f}")


def main() -> None:
    seeds = read_csv("manifests/seed_manifest_v0_3.csv")
    primary = read_csv(
        "data/processed/v0_3_primary_merged/confirmation_run_summaries.csv"
    )
    ablation = read_csv(
        "data/processed/v0_3_ablation_merged/confirmation_run_summaries.csv"
    )
    intervals = read_csv(
        "data/analysis/v0_3_final_analysis/primary_endpoint_intervals.csv"
    )
    summaries = read_csv(
        "data/analysis/v0_3_final_analysis/primary_condition_summary.csv"
    )
    verdict = read_csv(
        "data/analysis/v0_3_final_analysis/confirmatory_verdict.csv"
    )[0]
    audit = read_csv(
        "data/audits/PaperB_confirmatory_postrun_integrity_audit_v0_3.csv"
    )

    roles = Counter(row["role"] for row in seeds)
    require_equal("confirmatory seeds", roles["confirmatory_focal"], 72)
    require_equal("primary source rows", len(primary), 576)
    require_equal("ablation source rows", len(ablation), 432)

    replay = next(row for row in audit if row["check_id"] == "PRIMARY-EXACT-REPLAY")
    require_equal("exact replay", replay["detail"], "exact=288/288")

    sensing = next(
        row for row in intervals if row["metric"] == "causal_target_sensing_share"
    )
    require_close("target sensing difference", float(sensing["mean_difference"]), 0.11732711732711731)
    require_close("target sensing CI lower", float(sensing["ci_lower"]), 0.07216334013209014)
    require_close("target sensing CI upper", float(sensing["ci_upper"]), 0.163243006993007)
    require_close("target sensing SESOI", float(sensing["sesoi"]), 0.08)

    actual = next(
        row
        for row in summaries
        if row["relevance"] == "self_relevant" and row["condition"] == "actual_need"
    )
    yoked = next(
        row
        for row in summaries
        if row["relevance"] == "self_relevant" and row["condition"] == "yoked_need"
    )
    require_equal("actual replicated restoration", int(actual["replicated_restoration_count"]), 41)
    require_equal("yoked replicated restoration", int(yoked["replicated_restoration_count"]), 20)
    restoration = next(
        row for row in intervals if row["metric"] == "replicated_restoration"
    )
    require_close("replicated-restoration difference", float(restoration["mean_difference"]), 0.2916666666666667)

    require_equal("neutral false repairs", int(verdict["neutral_false_repairs"]), 0)
    require_equal("neutral safety N", int(verdict["neutral_n"]), 72)
    require_close("false-repair upper bound", float(verdict["false_repair_one_sided_95_upper"]), 0.04075368623063991)

    print("PASS public result verification")


if __name__ == "__main__":
    main()

