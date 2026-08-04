from __future__ import annotations

import argparse
import csv
from pathlib import Path

from constitutive_inquiry.protocol import UNIFIED_OBSERVATION_BUDGET, UNIFIED_SHIFT_OBSERVATION
from constitutive_inquiry.unified_experiment import run_unified_suite


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Paper B unified development conditions only.")
    parser.add_argument("--output", default="results/development/smoke")
    parser.add_argument("--seeds", default="0,6", help="Comma-separated development seeds. Do not use confirmatory seeds.")
    parser.add_argument("--conditions", default="actual_need,yoked_need,curiosity,no_need")
    parser.add_argument("--relevances", default="self_relevant,neutral")
    parser.add_argument("--yoke-map", default="", help="Optional frozen CSV with focal_seed,donor_seed columns.")
    parser.add_argument("--budget", type=int, default=UNIFIED_OBSERVATION_BUDGET)
    parser.add_argument("--shift", type=int, default=UNIFIED_SHIFT_OBSERVATION)
    parser.add_argument("--write-traces", action="store_true")
    parser.add_argument("--common-decoder", action="store_true")
    return parser.parse_args()


def load_yoke_map(path: str) -> dict[int, int] | None:
    if not path:
        return None
    mapping: dict[int, int] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            mapping[int(row["focal_seed"])] = int(row["donor_seed"])
    return mapping


def main() -> None:
    args = parse_args()
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    conditions = [value.strip() for value in args.conditions.split(",") if value.strip()]
    relevances = [value.strip() for value in args.relevances.split(",") if value.strip()]
    if any(seed >= 10_000 for seed in seeds):
        raise SystemExit("Development wrapper refuses seeds >=10000. Confirmatory execution requires a separately frozen wrapper.")
    yoke_map = load_yoke_map(args.yoke_map)
    if yoke_map and any(seed >= 10_000 for seed in yoke_map.values()):
        raise SystemExit("Development wrapper refuses yoke donors >=10000.")
    summaries, aggregates = run_unified_suite(
        Path(args.output),
        seeds,
        split="development",
        condition_ids=conditions,
        relevance_levels=relevances,
        yoke_map_override=yoke_map,
        write_traces=args.write_traces,
        run_common_decoder=args.common_decoder,
        budget=args.budget,
        shift=args.shift,
    )
    print(f"completed {len(summaries)} runs; wrote {len(aggregates)} aggregate rows to {args.output}")


if __name__ == "__main__":
    main()
