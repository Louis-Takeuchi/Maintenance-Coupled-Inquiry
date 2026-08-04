from __future__ import annotations

import csv
from pathlib import Path

from .agent import InquiryAgent, MODES, record_to_dict
from .crossworld import CrossWorldMemory
from .environment import HELDOUT_FAMILIES, RELEVANCE_LEVELS, TRAIN_FAMILIES, UnlabeledSelfWorld
from .metrics import aggregate, summarize_run


def train_crossworld_memory(
    output_dir: str | Path,
    seeds,
    budget: int = 360,
    shift: int = 28,
    write_traces: bool = False,
) -> tuple[CrossWorldMemory, CrossWorldMemory, list[dict]]:
    """Train relational and scalar-control memories on the same sequential worlds."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    relational = CrossWorldMemory(strategy="relational", revision_enabled=True)
    scalar = CrossWorldMemory(strategy="scalar", revision_enabled=False)
    summaries: list[dict] = []
    traces: list[dict] = []
    for seed in seeds:
        family = TRAIN_FAMILIES[seed % len(TRAIN_FAMILIES)]
        core_size = 3 + seed % 2
        world = UnlabeledSelfWorld(
            seed, "self_relevant", budget, shift, core_size,
            grammar_family=family, permute_labels=True, primitive_cardinality=6,
        )
        agent = InquiryAgent(
            "ungated_relational_generation", seed, "training",
            crossworld_memory=relational,
        )
        records = agent.run(world)
        summaries.append(summarize_run(records, world.spec, budget))
        relational.register_outcome(world, agent.model, records, allow_learning=True)
        scalar.register_outcome(world, agent.model, records, allow_learning=True)
        if write_traces:
            traces.extend(record_to_dict(row) for row in records)
    relational.save(output / "relational_memory.json")
    scalar.save(output / "scalar_rank_memory.json")
    _write(output / "training_run_summaries.csv", summaries)
    _write(output / "training_aggregate_metrics.csv", aggregate(summaries))
    if write_traces:
        _write(output / "training_step_traces.csv", traces)
    return relational, scalar, summaries


def _initial_memories(base: CrossWorldMemory, scalar: CrossWorldMemory, seed: int) -> dict[str, CrossWorldMemory | None]:
    frozen = base.clone()
    frozen.revision_enabled = False
    negative = base.negative_copy(seed)
    no_null = base.clone()
    no_null.revision_enabled = True
    return {
        "confidence_gated_relational_generation": base.clone(),
        "ungated_relational_generation": base.clone(),
        "reset_actual_generation": None,
        "sparse_reset_generation": None,
        "posterior_no_quarantine_generation": base.clone(),
        "quarantine_no_local_reservation_generation": base.clone(),
        "frozen_correct_memory_generation": frozen,
        "adversarial_wrong_memory_generation": negative,
        "oracle_family_generation": None,
        "no_null_confidence_gated_generation": no_null,
    }


def run_suite(
    output_dir: str | Path,
    seeds,
    split: str = "evaluation",
    write_traces: bool = False,
    budget: int = 360,
    shift: int = 28,
    relational_memory_path: str | Path | None = None,
    scalar_memory_path: str | Path | None = None,
    permute_labels: bool = True,
):
    """Run modes as separate sequential curricula so memory can revise over worlds."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if relational_memory_path is None:
        relational_memory_path = output.parent / "training" / "relational_memory.json"
    if scalar_memory_path is None:
        scalar_memory_path = output.parent / "training" / "scalar_rank_memory.json"
    base = CrossWorldMemory.load(relational_memory_path)
    scalar = CrossWorldMemory.load(scalar_memory_path)
    seed_list = list(seeds)
    memory_states = _initial_memories(base, scalar, seed_list[0] if seed_list else 0)
    summaries: list[dict] = []
    traces: list[dict] = []

    for mode in MODES:
        memory = memory_states[mode]
        for seed in seed_list:
            family = HELDOUT_FAMILIES[seed % len(HELDOUT_FAMILIES)]
            core_size = 5 + seed % 2
            primitive_cardinality = 5 if seed % 2 == 0 else 7
            for relevance in RELEVANCE_LEVELS:
                checkpoint = memory.clone() if memory is not None else None
                world = UnlabeledSelfWorld(
                    seed, relevance, budget, shift, core_size,
                    grammar_family=family, permute_labels=permute_labels,
                    primitive_cardinality=primitive_cardinality,
                    nonstationary=(seed % 4 == 3),
                )
                agent = InquiryAgent(mode, seed, split, crossworld_memory=memory)
                records = agent.run(world)
                summaries.append(summarize_run(records, world.spec, budget))
                if write_traces:
                    traces.extend(record_to_dict(row) for row in records)
                if relevance == "self_relevant" and memory is not None:
                    success = any(row.repair_correct for row in records)
                    if mode in {
                        "confidence_gated_relational_generation",
                        "quarantine_no_local_reservation_generation",
                        "adversarial_wrong_memory_generation",
                    }:
                        if success:
                            memory.register_outcome(world, agent.model, records, allow_learning=True)
                        else:
                            # Roll back memory changes from a failed transfer, quarantine
                            # the implicated mapping-template pair, then apply only decay.
                            mechanism = world.spec.causal_mechanism
                            proposed = next((row.proposed_intervention for row in reversed(records) if row.proposed_intervention), "")
                            sequence = tuple(proposed.split(">")) if proposed else ()
                            p2r, _, _ = memory.align(agent.model, mechanism, world.available_primitives)
                            if sequence and all(p in p2r for p in sequence):
                                memory.quarantine(tuple(p2r[p] for p in sequence), world.spec.grammar_family)
                            if checkpoint is not None:
                                memory.restore_from(checkpoint, preserve_quarantine=True)
                            memory.maintain(success=None)
                    elif mode in {"ungated_relational_generation", "posterior_no_quarantine_generation"}:
                        memory.register_outcome(world, agent.model, records, allow_learning=True)
                    elif mode == "no_null_confidence_gated_generation":
                        memory.register_outcome(world, agent.model, records, allow_learning=True)
                    elif mode == "frozen_correct_memory_generation":
                        pass
    aggregates = aggregate(summaries)
    suffix = "permuted" if permute_labels else "fixed"
    _write(output / f"{split}_{suffix}_run_summaries.csv", summaries)
    _write(output / f"{split}_{suffix}_aggregate_metrics.csv", aggregates)
    if write_traces:
        _write(output / f"{split}_{suffix}_step_traces.csv", traces)
    for mode, memory in memory_states.items():
        if memory is not None:
            memory.save(output / f"final_memory_{mode}.json")
    return summaries, aggregates


def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
