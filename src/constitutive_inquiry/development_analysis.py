from __future__ import annotations

from statistics import mean, median


DEFAULT_METRICS = (
    "mean_need_target_mass_share",
    "mean_need_true_core_mass_share",
    "mean_sensed_need_mass_share",
    "self_domain_observation_share",
    "causal_target_sensing_share",
    "causal_target_sensing_selectivity",
    "diagnosis_observations",
    "replicated_restoration",
    "false_null",
    "false_repair",
    "common_decoder_bridge_correct",
    "common_decoder_replicated_restoration",
)


def paired_contrasts(
    rows: list[dict[str, str]],
    left: str = "actual_need",
    right: str = "yoked_need",
    metrics: tuple[str, ...] = DEFAULT_METRICS,
) -> tuple[list[dict], list[dict]]:
    indexed = {(row["seed"], row["relevance"], row["mode"]): row for row in rows}
    pairs: list[dict] = []
    seeds_relevances = sorted({(row["seed"], row["relevance"]) for row in rows})
    for seed, relevance in seeds_relevances:
        left_row = indexed.get((seed, relevance, left))
        right_row = indexed.get((seed, relevance, right))
        if left_row is None or right_row is None:
            continue
        for metric in metrics:
            if metric not in left_row or metric not in right_row:
                continue
            difference = float(left_row[metric]) - float(right_row[metric])
            stratum = "|".join(
                str(left_row[field])
                for field in ("core_size", "grammar_family", "primitive_cardinality", "nonstationary", "topology")
                if field in left_row
            )
            pairs.append({
                "seed": seed,
                "relevance": relevance,
                "stratum": stratum,
                "left_condition": left,
                "right_condition": right,
                "metric": metric,
                "left_value": float(left_row[metric]),
                "right_value": float(right_row[metric]),
                "difference": difference,
            })

    summaries: list[dict] = []
    for relevance, metric in sorted({(row["relevance"], row["metric"]) for row in pairs}):
        group = [float(row["difference"]) for row in pairs if row["relevance"] == relevance and row["metric"] == metric]
        summaries.append({
            "relevance": relevance,
            "left_condition": left,
            "right_condition": right,
            "metric": metric,
            "n_pairs": len(group),
            "mean_difference": mean(group),
            "median_difference": median(group),
            "minimum_difference": min(group),
            "maximum_difference": max(group),
            "positive_fraction": sum(value > 0 for value in group) / len(group),
            "zero_fraction": sum(value == 0 for value in group) / len(group),
            "negative_fraction": sum(value < 0 for value in group) / len(group),
        })
    return pairs, summaries
