from __future__ import annotations

import argparse
import csv
from pathlib import Path

from constitutive_inquiry.agent import InquiryAgent, MODES
from constitutive_inquiry.crossworld import CrossWorldMemory
from constitutive_inquiry.environment import HELDOUT_FAMILIES, RELEVANCE_LEVELS, UnlabeledSelfWorld
from constitutive_inquiry.metrics import summarize_run


def load_rows(path: Path) -> list[dict]:
    return list(csv.DictReader(path.open(encoding="utf-8"))) if path.exists() else []


def append_row(path: Path, row: dict) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def make_memory(mode: str, relational_path: Path, seed: int) -> CrossWorldMemory | None:
    if mode.startswith("reset") or mode.startswith("sparse_reset") or mode.startswith("oracle"):
        return None
    base = CrossWorldMemory.load(relational_path)
    if mode == "adversarial_wrong_memory_generation":
        return base.negative_copy(seed)
    if mode == "frozen_correct_memory_generation":
        base.revision_enabled = False
    return base


def update_memory_after_world(
    mode: str,
    memory: CrossWorldMemory | None,
    checkpoint: CrossWorldMemory | None,
    world: UnlabeledSelfWorld,
    agent: InquiryAgent,
    records,
) -> None:
    if memory is None or world.relevance != "self_relevant":
        return
    success = any(row.repair_correct for row in records)
    gated_revision_modes = {
        "confidence_gated_relational_generation",
        "quarantine_no_local_reservation_generation",
        "adversarial_wrong_memory_generation",
    }
    if mode in gated_revision_modes:
        if success:
            memory.register_outcome(world, agent.model, records, allow_learning=True)
            return
        mechanism = world.spec.causal_mechanism
        proposed = next((row.proposed_intervention for row in reversed(records) if row.proposed_intervention), "")
        sequence = tuple(proposed.split(">")) if proposed else ()
        p2r, _, _ = memory.align(agent.model, mechanism, world.available_primitives)
        template = tuple(p2r[p] for p in sequence) if sequence and all(p in p2r for p in sequence) else ()
        if checkpoint is not None:
            memory.restore_from(checkpoint, preserve_quarantine=False)
        if template:
            memory.quarantine(template, world.spec.grammar_family)
        memory.maintain(success=None)
        return
    if mode in {"ungated_relational_generation", "posterior_no_quarantine_generation", "no_null_confidence_gated_generation"}:
        memory.register_outcome(world, agent.model, records, allow_learning=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=MODES, required=True)
    ap.add_argument("--seed-start", type=int, required=True)
    ap.add_argument("--seed-end", type=int, required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--relational-memory", required=True)
    ap.add_argument("--budget", type=int, default=360)
    ap.add_argument("--shift", type=int, default=28)
    ap.add_argument("--split", default="confirmation")
    ap.add_argument("--fixed-labels", action="store_true")
    args = ap.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / f"{args.mode}_run_summaries.csv"
    state_path = out / f"{args.mode}_memory_state.json"
    completed = {(int(r["seed"]), r["relevance"]) for r in load_rows(csv_path)}
    memory = CrossWorldMemory.load(state_path) if state_path.exists() else make_memory(args.mode, Path(args.relational_memory), args.seed_start)

    for seed in range(args.seed_start, args.seed_end):
        family = HELDOUT_FAMILIES[seed % len(HELDOUT_FAMILIES)]
        core_size = 5 + seed % 2
        cardinality = 5 if seed % 2 == 0 else 7
        for relevance in RELEVANCE_LEVELS:
            if (seed, relevance) in completed:
                continue
            checkpoint = memory.clone() if memory is not None else None
            world = UnlabeledSelfWorld(
                seed, relevance, args.budget, args.shift, core_size,
                grammar_family=family,
                permute_labels=not args.fixed_labels,
                primitive_cardinality=cardinality,
                nonstationary=(seed % 4 == 3),
            )
            agent = InquiryAgent(args.mode, seed, args.split, crossworld_memory=memory)
            records = agent.run(world)
            row = summarize_run(records, world.spec, args.budget)
            append_row(csv_path, row)
            update_memory_after_world(args.mode, memory, checkpoint, world, agent, records)
            if memory is not None:
                memory.save(state_path)
            print(
                args.mode, seed, relevance,
                row["organization_restored"], row["false_repair"],
                row["unique_sequences_evaluated"], row["mapping_trust"],
                row["wrong_memory_detected_before_repair"],
                flush=True,
            )


if __name__ == "__main__":
    main()
