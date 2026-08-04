#!/usr/bin/env python3
"""Regenerate selected frozen analysis tables into a noncanonical output dir.

This portability helper reuses the frozen v0.3 analysis functions but never
writes into data/analysis. It is not itself part of the frozen implementation.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from constitutive_inquiry.confirmatory_analysis import (
    CONFIRMATORY_BOOTSTRAP_REPLICATES,
    CONFIRMATORY_BOOTSTRAP_SEED,
    mean_difference,
    stratified_paired_bootstrap_mean_interval,
)
from constitutive_inquiry.development_analysis import paired_contrasts


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "data/processed/v0_3_primary_merged/confirmation_run_summaries.csv"
ABLATION = ROOT / "data/processed/v0_3_ablation_merged/confirmation_run_summaries.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def interval_for_pairs(
    pairs: list[dict], relevance: str, metric: str
) -> tuple[float, float, float, int]:
    group = [
        row
        for row in pairs
        if row["relevance"] == relevance and row["metric"] == metric
    ]
    interval = stratified_paired_bootstrap_mean_interval(
        group,
        seed=CONFIRMATORY_BOOTSTRAP_SEED,
        replicates=CONFIRMATORY_BOOTSTRAP_REPLICATES,
    )
    return mean_difference(group), interval.lower, interval.upper, len(group)


def summarize_condition(
    rows: list[dict[str, str]], conditions: list[str], relevance: str, metrics: list[str]
) -> list[dict]:
    output = []
    for condition in conditions:
        group = [
            row
            for row in rows
            if row["mode"] == condition and row["relevance"] == relevance
        ]
        summary: dict[str, object] = {
            "relevance": relevance,
            "condition": condition,
            "n": len(group),
        }
        for metric in metrics:
            values = [
                float(row[metric])
                for row in group
                if row.get(metric, "") not in ("", None)
            ]
            summary[f"{metric}_mean"] = sum(values) / len(values) if values else ""
            if values and all(value in (0.0, 1.0) for value in values):
                summary[f"{metric}_count"] = int(sum(values))
        output.append(summary)
    return output


def regenerate(output_dir: Path) -> None:
    primary = read_csv(PRIMARY)
    ablation = read_csv(ABLATION)

    paired_actual_yoked, _ = paired_contrasts(
        primary,
        left="actual_need",
        right="yoked_need",
        metrics=(
            "mean_need_target_mass_share",
            "causal_target_sensing_share",
            "causal_target_sensing_selectivity",
            "replicated_restoration",
            "diagnosis_observations",
            "bridge_decision_correct",
            "common_decoder_bridge_correct",
            "common_decoder_replicated_restoration",
            "common_decoder_false_repair",
            "common_decoder_observations",
        ),
    )
    selected = [
        ("mean_need_target_mass_share", "manipulation_check", 0.0),
        ("causal_target_sensing_share", "primary_mechanism", 0.08),
        ("causal_target_sensing_selectivity", "key_secondary", 0.08),
        ("replicated_restoration", "confirmatory_secondary", 0.10),
        ("diagnosis_observations", "secondary_latency", None),
        ("bridge_decision_correct", "secondary_accuracy", None),
        ("common_decoder_bridge_correct", "mediation_diagnostic", None),
        ("common_decoder_replicated_restoration", "mediation_diagnostic", None),
    ]
    primary_intervals = []
    for metric, role, sesoi in selected:
        value, lower, upper, count = interval_for_pairs(
            paired_actual_yoked, "self_relevant", metric
        )
        primary_intervals.append(
            {
                "world": "self_relevant",
                "contrast": "actual_need-yoked_need",
                "metric": metric,
                "role": role,
                "n_pairs": count,
                "mean_difference": value,
                "ci_lower": lower,
                "ci_upper": upper,
                "sesoi": sesoi if sesoi is not None else "",
                "bootstrap_seed": CONFIRMATORY_BOOTSTRAP_SEED,
                "bootstrap_replicates": CONFIRMATORY_BOOTSTRAP_REPLICATES,
            }
        )
    write_csv(output_dir / "primary_endpoint_intervals.csv", primary_intervals)

    primary_summary = []
    for relevance in ["self_relevant", "neutral"]:
        primary_summary += summarize_condition(
            primary,
            ["actual_need", "yoked_need", "curiosity", "no_need"],
            relevance,
            [
                "causal_target_sensing_share",
                "causal_target_sensing_selectivity",
                "bridge_decision_correct",
                "explicit_no_bridge",
                "false_repair",
                "replicated_restoration",
                "diagnosis_observations",
                "common_decoder_bridge_correct",
                "common_decoder_false_repair",
                "common_decoder_replicated_restoration",
            ],
        )
    write_csv(output_dir / "primary_condition_summary.csv", primary_summary)

    common_decoder = []
    for relevance in ["self_relevant", "neutral"]:
        for metric in [
            "common_decoder_bridge_correct",
            "common_decoder_replicated_restoration",
            "common_decoder_false_repair",
            "common_decoder_observations",
        ]:
            value, lower, upper, count = interval_for_pairs(
                paired_actual_yoked, relevance, metric
            )
            common_decoder.append(
                {
                    "world": relevance,
                    "contrast": "actual_trace-yoked_trace",
                    "metric": metric,
                    "n_pairs": count,
                    "mean_difference": value,
                    "ci_lower": lower,
                    "ci_upper": upper,
                    "interpretation": "trace_source_mediation_diagnostic_not_natural_direct_effect",
                }
            )
    write_csv(output_dir / "common_decoder_diagnostics.csv", common_decoder)

    ablation_summary = []
    for condition, relevance in [
        ("correlation_self_model", "self_relevant"),
        ("no_null", "neutral"),
        ("no_bridge_validation", "neutral"),
        ("no_null_no_validation", "neutral"),
        ("passive_only", "self_relevant"),
        ("pair_limited", "self_relevant"),
    ]:
        ablation_summary += summarize_condition(
            ablation,
            [condition],
            relevance,
            [
                "core_precision",
                "core_recall",
                "diagnosis_made",
                "bridge_decision_correct",
                "explicit_no_bridge",
                "repair_attempted",
                "false_repair",
                "organization_restored",
                "replicated_restoration",
                "exact_program",
                "functional_program",
                "causal_target_sensing_share",
                "diagnosis_observations",
            ],
        )
    write_csv(output_dir / "ablation_condition_summary.csv", ablation_summary)

    primary_index = {
        (row["seed"], row["relevance"]): row
        for row in primary
        if row["mode"] == "actual_need"
    }
    ablation_index = {
        (row["seed"], row["relevance"], row["mode"]): row for row in ablation
    }
    specs = {
        "correlation_self_model": (
            "self_relevant",
            [
                "core_precision",
                "core_recall",
                "bridge_decision_correct",
                "replicated_restoration",
                "causal_target_sensing_share",
            ],
        ),
        "no_null": (
            "neutral",
            [
                "diagnosis_made",
                "explicit_no_bridge",
                "decision_correct",
                "false_repair",
                "repair_attempted",
            ],
        ),
        "no_bridge_validation": (
            "neutral",
            [
                "explicit_no_bridge",
                "false_repair",
                "repair_attempted",
                "organization_restored",
                "decision_correct",
            ],
        ),
        "no_null_no_validation": (
            "neutral",
            [
                "explicit_no_bridge",
                "false_repair",
                "repair_attempted",
                "organization_restored",
                "decision_correct",
            ],
        ),
        "passive_only": (
            "self_relevant",
            [
                "diagnosis_made",
                "bridge_decision_correct",
                "replicated_restoration",
                "diagnosis_observations",
            ],
        ),
        "pair_limited": (
            "self_relevant",
            [
                "exact_program",
                "functional_program",
                "bridge_decision_correct",
                "replicated_restoration",
                "diagnosis_observations",
            ],
        ),
    }
    ablation_pairs = []
    for condition, (relevance, metrics) in specs.items():
        for metric in metrics:
            rows = []
            for seed in range(30000, 30072):
                actual = primary_index[(str(seed), relevance)]
                comparison = ablation_index[(str(seed), relevance, condition)]
                stratum = "|".join(
                    actual[field]
                    for field in (
                        "core_size",
                        "grammar_family",
                        "primitive_cardinality",
                        "nonstationary",
                        "topology",
                    )
                )
                rows.append(
                    {
                        "seed": seed,
                        "stratum": stratum,
                        "difference": float(actual[metric]) - float(comparison[metric]),
                    }
                )
            interval = stratified_paired_bootstrap_mean_interval(
                rows,
                seed=CONFIRMATORY_BOOTSTRAP_SEED,
                replicates=CONFIRMATORY_BOOTSTRAP_REPLICATES,
            )
            difference = sum(row["difference"] for row in rows) / len(rows)
            lower_better = metric in {
                "false_repair",
                "repair_attempted",
                "diagnosis_observations",
            }
            ablation_pairs.append(
                {
                    "world": relevance,
                    "contrast": f"actual_need-{condition}",
                    "metric": metric,
                    "n_pairs": len(rows),
                    "mean_difference": difference,
                    "ci_lower": interval.lower,
                    "ci_upper": interval.upper,
                    "preferred_direction": (
                        "negative_for_actual" if lower_better else "positive_for_actual"
                    ),
                    "interpretation": "descriptive_ablation_only_no_general_necessity_claim",
                    "bootstrap_seed": CONFIRMATORY_BOOTSTRAP_SEED,
                    "bootstrap_replicates": CONFIRMATORY_BOOTSTRAP_REPLICATES,
                }
            )
    ablation_pairs.sort(key=lambda row: (row["contrast"], row["metric"]))
    write_csv(output_dir / "ablation_paired_diagnostics.csv", ablation_pairs)

    print(f"Wrote five reproduced tables to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "build/reproduced-analysis",
        help="noncanonical destination (default: build/reproduced-analysis)",
    )
    args = parser.parse_args()
    regenerate(args.output.resolve())


if __name__ == "__main__":
    main()

