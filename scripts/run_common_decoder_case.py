from __future__ import annotations

import argparse
import csv
from pathlib import Path

from constitutive_inquiry.agent import InquiryAgent
from constitutive_inquiry.metrics import summarize_run
from constitutive_inquiry.protocol import UNIFIED_OBSERVATION_BUDGET, UNIFIED_SHIFT_OBSERVATION, get_condition
from constitutive_inquiry.replay import run_common_decoder_replay, source_evidence_prefix
from constitutive_inquiry.unified_experiment import (
    collect_actual_need_trace,
    make_world,
    permute_yoked_trace,
    yoke_component_shift,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one development common-decoder case.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--relevance", choices=("self_relevant", "neutral"), required=True)
    parser.add_argument("--condition", choices=("actual_need", "yoked_need"), required=True)
    parser.add_argument("--donor-seed", type=int)
    parser.add_argument("--budget", type=int, default=UNIFIED_OBSERVATION_BUDGET)
    parser.add_argument("--shift", type=int, default=UNIFIED_SHIFT_OBSERVATION)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed >= 10_000 or (args.donor_seed is not None and args.donor_seed >= 10_000):
        raise SystemExit("Development case runner refuses seeds >=10000.")
    condition = get_condition(args.condition)
    yoked_trace = None
    donor = ""
    component_shift = ""
    if args.condition == "yoked_need":
        if args.donor_seed is None or args.donor_seed == args.seed:
            raise SystemExit("yoked_need requires a different --donor-seed")
        donor = args.donor_seed
        donor_trace = collect_actual_need_trace(
            args.donor_seed,
            args.relevance,
            "development_yoke_donor",
            args.budget,
            args.shift,
        )
        yoked_trace = permute_yoked_trace(donor_trace, args.seed, args.donor_seed)
        component_shift = yoke_component_shift(args.seed, args.donor_seed)

    world = make_world(args.seed, args.relevance, args.budget, args.shift)
    agent = InquiryAgent(
        "sparse_reset_generation",
        args.seed,
        "development",
        yoked_trace=yoked_trace,
        condition=condition,
    )
    records = agent.run(world)
    summary = summarize_run(records, world.spec, args.budget)
    actions, expected, side_effects = source_evidence_prefix(agent)
    replay = run_common_decoder_replay(
        args.seed,
        args.relevance,
        args.budget,
        args.shift,
        actions,
        expected,
        side_effects,
    )
    summary.update(replay.to_summary_fields())
    summary["yoke_donor_seed"] = donor
    summary["yoke_component_shift"] = component_shift

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary))
        writer.writeheader()
        writer.writerow(summary)
    print(path)


if __name__ == "__main__":
    main()
