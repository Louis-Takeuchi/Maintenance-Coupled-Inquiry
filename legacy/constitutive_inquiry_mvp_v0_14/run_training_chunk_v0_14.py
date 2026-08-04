from __future__ import annotations

import argparse
import csv
from pathlib import Path

from constitutive_inquiry.agent import InquiryAgent
from constitutive_inquiry.crossworld import CrossWorldMemory
from constitutive_inquiry.environment import TRAIN_FAMILIES, UnlabeledSelfWorld
from constitutive_inquiry.metrics import summarize_run


def append_row(path: Path, row: dict) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-start", type=int, required=True)
    ap.add_argument("--seed-end", type=int, required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--budget", type=int, default=360)
    ap.add_argument("--shift", type=int, default=28)
    args = ap.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rel_path = out / "relational_memory.json"
    scalar_path = out / "scalar_rank_memory.json"
    relational = CrossWorldMemory.load(rel_path) if rel_path.exists() else CrossWorldMemory(strategy="relational")
    scalar = CrossWorldMemory.load(scalar_path) if scalar_path.exists() else CrossWorldMemory(strategy="scalar", revision_enabled=False)
    csv_path = out / "training_run_summaries.csv"
    completed = set()
    if csv_path.exists():
        completed = {int(row["seed"]) for row in csv.DictReader(csv_path.open(encoding="utf-8"))}
    for seed in range(args.seed_start, args.seed_end):
        if seed in completed:
            continue
        family = TRAIN_FAMILIES[seed % len(TRAIN_FAMILIES)]
        world = UnlabeledSelfWorld(
            seed, "self_relevant", args.budget, args.shift, 3 + seed % 2,
            grammar_family=family, permute_labels=True, primitive_cardinality=6,
        )
        # Training inquiry is local/reset. Successful programs are then registered
        # in both relational and scalar control memories from identical evidence.
        agent = InquiryAgent("reset_actual_generation", seed, "training", crossworld_memory=relational)
        records = agent.run(world)
        row = summarize_run(records, world.spec, args.budget)
        relational.register_outcome(world, agent.model, records, allow_learning=True)
        scalar.register_outcome(world, agent.model, records, allow_learning=True)
        append_row(csv_path, row)
        relational.save(rel_path)
        scalar.save(scalar_path)
        print(seed, row["grammar_family"], row["organization_restored"], row["unique_sequences_evaluated"], flush=True)


if __name__ == "__main__":
    main()
