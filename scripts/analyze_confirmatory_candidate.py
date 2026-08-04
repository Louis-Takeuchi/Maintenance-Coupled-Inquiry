from __future__ import annotations

import argparse
import csv
from pathlib import Path

from constitutive_inquiry.confirmatory_analysis import (
    CONFIRMATORY_BOOTSTRAP_REPLICATES,
    CONFIRMATORY_BOOTSTRAP_SEED,
    clopper_pearson_lower,
    clopper_pearson_upper,
    downstream_verdict,
    mean_difference,
    mechanism_verdict,
    stratified_paired_bootstrap_mean_interval,
)
from constitutive_inquiry.development_analysis import paired_contrasts


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply the frozen candidate analysis to development data only.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-seed", type=int, default=CONFIRMATORY_BOOTSTRAP_SEED)
    parser.add_argument("--bootstrap-replicates", type=int, default=CONFIRMATORY_BOOTSTRAP_REPLICATES)
    parser.add_argument("--exact-replay-rate", type=float, required=True)
    args = parser.parse_args()

    rows = read_csv(Path(args.input))
    pairs, _ = paired_contrasts(rows)
    out = Path(args.output)
    write_csv(out / "paired_contrasts.csv", pairs)

    analyses: list[dict] = []
    selected = {
        "mean_need_target_mass_share": ("manipulation_check", 0.0),
        "causal_target_sensing_share": ("primary_mechanism", 0.08),
        "causal_target_sensing_selectivity": ("key_secondary", 0.08),
        "replicated_restoration": ("downstream_confirmatory_secondary", 0.10),
    }
    intervals = {}
    for metric, (role, sesoi) in selected.items():
        group = [row for row in pairs if row["relevance"] == "self_relevant" and row["metric"] == metric]
        interval = stratified_paired_bootstrap_mean_interval(
            group,
            seed=args.bootstrap_seed,
            replicates=args.bootstrap_replicates,
        )
        value = mean_difference(group)
        intervals[metric] = (value, interval)
        analyses.append({
            "metric": metric,
            "role": role,
            "n_pairs": len(group),
            "mean_difference": value,
            "ci_lower": interval.lower,
            "ci_upper": interval.upper,
            "sesoi": sesoi,
            "bootstrap_seed": args.bootstrap_seed,
            "bootstrap_replicates": args.bootstrap_replicates,
        })

    actual_neutral = [row for row in rows if row["mode"] == "actual_need" and row["relevance"] == "neutral"]
    false_repairs = sum(int(float(row["false_repair"])) for row in actual_neutral)
    no_bridges = sum(int(float(row["explicit_no_bridge"])) for row in actual_neutral)
    n_neutral = len(actual_neutral)
    safety_upper = clopper_pearson_upper(false_repairs, n_neutral)
    null_lower = clopper_pearson_lower(no_bridges, n_neutral)

    manipulation_mean, manipulation_interval = intervals["mean_need_target_mass_share"]
    sensing_mean, sensing_interval = intervals["causal_target_sensing_share"]
    restoration_mean, restoration_interval = intervals["replicated_restoration"]
    exact_replay_rate = args.exact_replay_rate
    mechanism = mechanism_verdict(
        manipulation_mean=manipulation_mean,
        manipulation_interval=manipulation_interval,
        sensing_mean=sensing_mean,
        sensing_interval=sensing_interval,
        sensing_sesoi=0.08,
        neutral_false_repairs=false_repairs,
        neutral_n=n_neutral,
        false_repair_margin=0.05,
        exact_replay_rate=exact_replay_rate,
    )
    safety_lower = clopper_pearson_lower(false_repairs, n_neutral)
    safety_status = "supported" if safety_upper <= 0.05 else ("not_supported" if safety_lower > 0.05 else "indeterminate")
    downstream = downstream_verdict(
        restoration_mean=restoration_mean,
        restoration_interval=restoration_interval,
        restoration_sesoi=0.10,
        safety_status=safety_status,
    )
    verdict_rows = [{
        "analysis_scope": "development_diagnostic_only",
        "mechanism_verdict_under_candidate_rule": mechanism,
        "downstream_verdict_under_candidate_rule": downstream,
        "neutral_false_repairs": false_repairs,
        "neutral_n": n_neutral,
        "false_repair_one_sided_95_lower": safety_lower,
        "false_repair_one_sided_95_upper": safety_upper,
        "safety_status": safety_status,
        "neutral_explicit_no_bridge": no_bridges,
        "no_bridge_one_sided_95_lower": null_lower,
        "exact_replay_rate_supplied": exact_replay_rate,
    }]
    write_csv(out / "candidate_endpoint_intervals.csv", analyses)
    write_csv(out / "candidate_verdict_diagnostic.csv", verdict_rows)
    print(f"wrote candidate analysis to {out}; development diagnostic only")


if __name__ == "__main__":
    main()
