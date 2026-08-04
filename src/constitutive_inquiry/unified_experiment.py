from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .agent import InquiryAgent, record_to_dict
from .environment import HELDOUT_FAMILIES, N_INTERNAL, RELEVANCE_LEVELS, UnlabeledSelfWorld
from .metrics import aggregate, summarize_run
from .protocol import (
    CONDITIONS, PRIMARY_CONDITIONS, ConditionSpec, NeedPolicy,
    UNIFIED_MEMORY_CAPACITY_BUDGET, UNIFIED_OBSERVATION_BUDGET,
    UNIFIED_SHIFT_OBSERVATION, endpoint_registry_rows, get_condition,
)


@dataclass(frozen=True)
class WorldConfig:
    seed: int
    core_size: int
    grammar_family: str
    primitive_cardinality: int
    nonstationary: bool
    topology: str

    def stratum(self) -> tuple:
        return (
            self.core_size,
            self.grammar_family,
            self.primitive_cardinality,
            self.nonstationary,
            self.topology,
        )


def evaluation_world_config(seed: int) -> WorldConfig:
    """Return the frozen v0.14 evaluation configuration for a seed."""

    probe = UnlabeledSelfWorld(
        seed,
        "self_relevant",
        observation_budget=1,
        shift_observation=0,
        core_size=5 + seed % 2,
        grammar_family=HELDOUT_FAMILIES[seed % len(HELDOUT_FAMILIES)],
        permute_labels=True,
        primitive_cardinality=5 if seed % 2 == 0 else 7,
        nonstationary=(seed % 4 == 3),
    )
    return WorldConfig(
        seed=seed,
        core_size=probe.spec.core_size,
        grammar_family=probe.spec.grammar_family,
        primitive_cardinality=len(probe.spec.available_primitives),
        nonstationary=probe.spec.nonstationary,
        topology=probe.spec.topology,
    )


def build_yoke_map(seeds: Iterable[int]) -> dict[int, int]:
    """Pair each focal seed to a different seed in the same frozen stratum.

    The mapping is deterministic and must be written to a manifest before any
    confirmatory execution. A singleton stratum is rejected rather than silently
    relaxing the matching constraints.
    """

    seed_list = sorted(set(int(seed) for seed in seeds))
    groups: dict[tuple, list[int]] = {}
    for seed in seed_list:
        config = evaluation_world_config(seed)
        groups.setdefault(config.stratum(), []).append(seed)
    mapping: dict[int, int] = {}
    for stratum, members in sorted(groups.items(), key=lambda row: row[0]):
        if len(members) < 2:
            raise ValueError(f"cannot yoke singleton stratum {stratum}: {members}")
        ordered = sorted(members)
        for index, seed in enumerate(ordered):
            mapping[seed] = ordered[(index + 1) % len(ordered)]
    return mapping



def yoke_component_shift(focal_seed: int, donor_seed: int) -> int:
    """Deterministic non-zero cyclic component shift for a yoked need vector."""

    return 1 + ((focal_seed * 37 + donor_seed * 19 + 11) % (N_INTERNAL - 1))


def permute_yoked_trace(trace: list[list[float]], focal_seed: int, donor_seed: int) -> list[list[float]]:
    """Break component-to-self alignment while preserving each donor time series exactly.

    A cyclic derangement has no fixed component. Total need at every time point and
    the temporal structure of every donor component are preserved.
    """

    shift = yoke_component_shift(focal_seed, donor_seed)
    return [[row[(index - shift) % N_INTERNAL] for index in range(N_INTERNAL)] for row in trace]

def make_world(seed: int, relevance: str, budget: int, shift: int) -> UnlabeledSelfWorld:
    config = evaluation_world_config(seed)
    return UnlabeledSelfWorld(
        seed,
        relevance,
        observation_budget=budget,
        shift_observation=shift,
        core_size=config.core_size,
        grammar_family=config.grammar_family,
        permute_labels=True,
        primitive_cardinality=config.primitive_cardinality,
        nonstationary=config.nonstationary,
        memory_capacity_budget=UNIFIED_MEMORY_CAPACITY_BUDGET,
    )


def collect_actual_need_trace(seed: int, relevance: str, split: str, budget: int, shift: int) -> list[list[float]]:
    world = make_world(seed, relevance, budget, shift)
    condition = get_condition("actual_need")
    agent = InquiryAgent("sparse_reset_generation", seed, split, condition=condition)
    agent.run(world)
    return [list(row) for row in agent.need_history] or [[0.0] * N_INTERNAL]


def run_unified_suite(
    output_dir: str | Path,
    seeds: Iterable[int],
    split: str = "development",
    condition_ids: Sequence[str] | None = None,
    relevance_levels: Sequence[str] | None = None,
    yoke_map_override: dict[int, int] | None = None,
    write_traces: bool = False,
    run_common_decoder: bool = False,
    budget: int = UNIFIED_OBSERVATION_BUDGET,
    shift: int = UNIFIED_SHIFT_OBSERVATION,
) -> tuple[list[dict], list[dict]]:
    """Run paired primary/ablation conditions without cross-world memory.

    This function does not enforce a particular seed range. Confirmatory seed
    protection is handled by the pre-run manifest and execution wrapper; during
    implementation only development seeds should be supplied.
    """

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    seed_list = sorted(set(int(seed) for seed in seeds))
    selected = list(condition_ids or PRIMARY_CONDITIONS.keys())
    condition_specs = [get_condition(condition_id) for condition_id in selected]
    selected_relevances = list(relevance_levels or RELEVANCE_LEVELS)
    invalid_relevances = sorted(set(selected_relevances) - set(RELEVANCE_LEVELS))
    if invalid_relevances:
        raise ValueError(f"unknown relevance levels: {invalid_relevances}")
    needs_yoke = any(c.need_policy == NeedPolicy.YOKED for c in condition_specs)
    if needs_yoke and yoke_map_override is not None:
        yoke_map = {int(focal): int(donor) for focal, donor in yoke_map_override.items()}
        missing = [seed for seed in seed_list if seed not in yoke_map]
        if missing:
            raise ValueError(f"yoke map missing focal seeds: {missing}")
        for focal in seed_list:
            donor = yoke_map[focal]
            if donor == focal:
                raise ValueError(f"yoke donor must differ from focal seed {focal}")
            if evaluation_world_config(focal).stratum() != evaluation_world_config(donor).stratum():
                raise ValueError(f"yoke stratum mismatch: focal={focal}, donor={donor}")
    else:
        yoke_map = build_yoke_map(seed_list) if needs_yoke else {}
    donor_cache: dict[tuple[int, str], list[list[float]]] = {}
    summaries: list[dict] = []
    traces: list[dict] = []

    _write(output / f"{split}_condition_registry.csv", [condition.to_dict() for condition in condition_specs])
    _write(output / f"{split}_endpoint_registry.csv", endpoint_registry_rows())
    if yoke_map:
        _write(
            output / f"{split}_yoke_map.csv",
            [
                {
                    "focal_seed": focal,
                    "donor_seed": donor,
                    "stratum": "|".join(map(str, evaluation_world_config(focal).stratum())),
                    "component_shift": yoke_component_shift(focal, donor),
                }
                for focal, donor in sorted(yoke_map.items())
            ],
        )

    for seed in seed_list:
        for relevance in selected_relevances:
            for condition in condition_specs:
                yoked_trace = None
                if condition.need_policy == NeedPolicy.YOKED:
                    donor = yoke_map[seed]
                    key = (donor, relevance)
                    if key not in donor_cache:
                        donor_cache[key] = collect_actual_need_trace(donor, relevance, f"{split}_yoke_donor", budget, shift)
                    yoked_trace = permute_yoked_trace(donor_cache[key], seed, donor)
                world = make_world(seed, relevance, budget, shift)
                agent = InquiryAgent(
                    "sparse_reset_generation",
                    seed,
                    split,
                    yoked_trace=yoked_trace,
                    condition=condition,
                )
                records = agent.run(world)
                summary = summarize_run(records, world.spec, budget)
                if run_common_decoder:
                    from .replay import run_common_decoder_replay, source_evidence_prefix
                    replay_actions, replay_expected, replay_side_effects = source_evidence_prefix(agent)
                    replay_result = run_common_decoder_replay(
                        seed, relevance, budget, shift, replay_actions, replay_expected, replay_side_effects
                    )
                    summary.update(replay_result.to_summary_fields())
                summary["yoke_donor_seed"] = yoke_map.get(seed, "") if condition.need_policy == NeedPolicy.YOKED else ""
                summary["yoke_component_shift"] = yoke_component_shift(seed, yoke_map[seed]) if condition.need_policy == NeedPolicy.YOKED else ""
                summaries.append(summary)
                if write_traces:
                    traces.extend(record_to_dict(row) for row in records)

    aggregates = aggregate(summaries)
    _write(output / f"{split}_run_summaries.csv", summaries)
    _write(output / f"{split}_aggregate_metrics.csv", aggregates)
    if write_traces:
        _write(output / f"{split}_step_traces.csv", traces)
    return summaries, aggregates


def condition_registry_rows() -> list[dict]:
    return [CONDITIONS[key].to_dict() for key in sorted(CONDITIONS)]


def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
