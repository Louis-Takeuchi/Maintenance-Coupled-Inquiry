from __future__ import annotations

import argparse

from constitutive_inquiry.experiment import run_suite, train_crossworld_memory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train", "evaluate"), default="evaluate")
    parser.add_argument("--split", default="evaluation")
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--seed-end", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--relational-memory")
    parser.add_argument("--scalar-memory")
    parser.add_argument("--budget", type=int)
    parser.add_argument("--shift", type=int, default=28)
    parser.add_argument("--fixed-labels", action="store_true")
    parser.add_argument("--write-traces", action="store_true")
    args = parser.parse_args()
    seeds = range(args.seed_start, args.seed_end)
    if args.phase == "train":
        train_crossworld_memory(
            args.output, seeds, args.budget or 360, args.shift, args.write_traces,
        )
    else:
        run_suite(
            args.output, seeds, args.split, args.write_traces, args.budget or 360,
            args.shift, args.relational_memory, args.scalar_memory, not args.fixed_labels,
        )


if __name__ == "__main__":
    main()
