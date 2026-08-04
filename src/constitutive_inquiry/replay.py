from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence

from .agent import SideEffectRecord
from .environment import Action, N_INTERNAL, Observation
from .model import Diagnosis, InquiryModel
from .self_model import SelfModelLearner
from .unified_experiment import make_world


@dataclass(frozen=True)
class CommonDecoderResult:
    exact_replay_match: bool
    replayed_observations: int
    diagnosis_made: bool
    diagnosis_kind: str
    diagnosis_observations: int
    mechanism_correct: bool
    bridge_correct: bool
    validation_attempted: bool
    validation_passed: bool
    repair_attempted: bool
    repair_correct: bool
    organization_restored: bool
    replication_attempted: bool
    replication_success: bool
    replicated_restoration: bool
    false_repair: bool

    def to_summary_fields(self) -> dict:
        return {
            "replay_exact_match": int(self.exact_replay_match),
            "replayed_observations": self.replayed_observations,
            "common_decoder_diagnosis_made": int(self.diagnosis_made),
            "common_decoder_kind": self.diagnosis_kind,
            "common_decoder_observations": self.diagnosis_observations,
            "common_decoder_mechanism_correct": int(self.mechanism_correct),
            "common_decoder_bridge_correct": int(self.bridge_correct),
            "common_decoder_validation_attempted": int(self.validation_attempted),
            "common_decoder_validation_passed": int(self.validation_passed),
            "common_decoder_repair_attempted": int(self.repair_attempted),
            "common_decoder_repair_correct": int(self.repair_correct),
            "common_decoder_organization_restored": int(self.organization_restored),
            "common_decoder_replication_attempted": int(self.replication_attempted),
            "common_decoder_replication_success": int(self.replication_success),
            "common_decoder_replicated_restoration": int(self.replicated_restoration),
            "common_decoder_false_repair": int(self.false_repair),
        }


def _empty_side_effect() -> SideEffectRecord:
    return SideEffectRecord(
        validation_attempted=False,
        validation_mechanism="",
        validation_intervention=(),
        validation_passed=False,
        validation_effect=0.0,
        validation_bypassed=False,
        repair_attempted=False,
        restore_operator="",
        repair_correct=False,
        replication_attempted=False,
        replication_intervention=(),
    )


def source_evidence_prefix(agent) -> tuple[list[Action], list[Observation], list[SideEffectRecord]]:
    """Return the source evidence prefix without applying its accepted decision.

    Failed validation side effects before the first accepted diagnosis are retained,
    because they can change later observations. Validation/repair/replication on the
    accepted diagnosis step are removed: the common decoder must make those decisions
    itself from the same evidence state.
    """

    stop = len(agent.records)
    accepted_index: int | None = None
    for index, row in enumerate(agent.records):
        if row.diagnosis_made:
            stop = index + 1
            accepted_index = index
            break
    side_effects = list(agent.side_effect_history[:stop])
    if accepted_index is not None and side_effects:
        side_effects[-1] = _empty_side_effect()
    return (
        list(agent.action_history[:stop]),
        list(agent.observation_history[:stop]),
        side_effects,
    )


def _replay_source_side_effect(world, event: SideEffectRecord) -> bool:
    exact = True
    if event.validation_attempted:
        passed, effect, _ = world.validate_bridge(event.validation_mechanism, event.validation_intervention)
        exact = exact and passed == event.validation_passed and effect == event.validation_effect
    elif event.validation_bypassed:
        exact = exact and event.validation_passed
    if event.repair_attempted:
        result = world.repair_sequence(event.validation_intervention, event.restore_operator)
        exact = exact and result.correct == event.repair_correct
    if event.replication_attempted:
        replication = world.replication_test(event.replication_intervention)
        exact = exact and replication.attempted
    return exact


def _candidate_map(model: InquiryModel) -> dict[str, tuple[str, ...]]:
    candidates: dict[str, tuple[str, ...]] = {}
    for mechanism in model.active_mechanisms(2):
        ranked = model.ranked_sequences(mechanism)
        if ranked:
            candidates[mechanism] = ranked[0]
    return candidates


def _evidence_signature(
    model: InquiryModel,
    self_prob: list[float],
    candidates: dict[str, tuple[str, ...]],
) -> tuple:
    """Compact signature of evidence that can change a diagnosis verdict."""

    rows = []
    for mechanism in sorted(candidates):
        intervention = candidates[mechanism]
        suppression, n_base, n_treated = model.candidate_suppression(mechanism, intervention)
        effect, n_off, n_on = model.bridge_evidence(mechanism, intervention, self_prob)
        rows.append(
            (
                mechanism,
                intervention,
                round(suppression, 12),
                n_base,
                n_treated,
                round(effect, 12),
                n_off,
                n_on,
            )
        )
    return tuple(rows)


def _need_blind_repair(world, diagnosis: Diagnosis, self_prob: list[float]) -> tuple[bool, float, str]:
    priority = [0.68 * (i == diagnosis.target_index) + 0.32 * self_prob[i] for i in range(N_INTERNAL)]
    best_operator, best_score = next(iter(world.restore_targets)), -1e9
    for operator in world.restore_targets:
        probe = world.probe_restore(operator)
        score = sum(delta * weight for delta, weight in zip(probe.delta, priority))
        if score > best_score:
            best_operator, best_score = operator, score
    result = world.repair_sequence(diagnosis.intervention, best_operator)
    return result.correct, result.improvement, best_operator


def _decision_world_at_observation(
    seed: int,
    relevance: str,
    budget: int,
    shift: int,
    actions: Sequence[Action],
    side_effects: Sequence[SideEffectRecord],
    diagnosis_position: int,
):
    """Reconstruct world state immediately after the diagnosis observation."""

    world = make_world(seed, relevance, budget, shift)
    for index in range(diagnosis_position + 1):
        world.observe(actions[index])
        if index < diagnosis_position:
            _replay_source_side_effect(world, side_effects[index])
    return world


def run_common_decoder_replay(
    seed: int,
    relevance: str,
    budget: int,
    shift: int,
    actions: Sequence[Action],
    expected: Sequence[Observation],
    side_effects: Sequence[SideEffectRecord],
) -> CommonDecoderResult:
    """Exact trace replay followed by a policy- and need-blind decoder."""

    if not (len(actions) == len(expected) == len(side_effects)):
        raise ValueError("replay trace lengths differ")
    source_world = make_world(seed, relevance, budget, shift)
    replayed: list[Observation] = []
    exact = True
    for action, expected_observation, event in zip(actions, expected, side_effects):
        observation = source_world.observe(action)
        replayed.append(observation)
        exact = exact and observation == expected_observation
        exact = exact and _replay_source_side_effect(source_world, event)

    self_model = SelfModelLearner("causal")
    model = InquiryModel(allow_null=True)
    diagnosis: Diagnosis | None = None
    diagnosis_index = budget + 1
    diagnosis_position = -1
    diagnosis_self_prob: list[float] | None = None
    previous_signature: tuple | None = None
    any_validation_attempted = False
    accepted_validation_passed = False

    for position, observation in enumerate(replayed):
        self_model.update(observation)
        model.update(observation)
        candidates = _candidate_map(model)
        if not candidates:
            continue
        signature = _evidence_signature(model, self_model.core_probabilities, candidates)
        if signature == previous_signature:
            continue
        previous_signature = signature
        eligible = any(
            model.candidate_suppression(mechanism, intervention)[1] > 0
            and model.candidate_suppression(mechanism, intervention)[2] >= 3
            for mechanism, intervention in candidates.items()
        )
        if not eligible:
            continue
        candidate = model.diagnose(self_model.core_probabilities, candidates)
        if candidate is None:
            continue
        if candidate.kind == "bridge":
            any_validation_attempted = True
            validation_world = make_world(seed, relevance, budget, shift)
            validation_world.observation_count = observation.index + 1
            passed, _, _ = validation_world.validate_bridge(candidate.mechanism, candidate.intervention)
            if not passed:
                model.register_validation_failure(candidate)
                continue
            accepted_validation_passed = True
        diagnosis = candidate
        diagnosis_index = observation.index + 1
        diagnosis_position = position
        diagnosis_self_prob = list(self_model.core_probabilities)
        break

    if diagnosis is None:
        return CommonDecoderResult(
            exact_replay_match=exact,
            replayed_observations=len(replayed),
            diagnosis_made=False,
            diagnosis_kind="",
            diagnosis_observations=budget + 1,
            mechanism_correct=False,
            bridge_correct=False,
            validation_attempted=any_validation_attempted,
            validation_passed=False,
            repair_attempted=False,
            repair_correct=False,
            organization_restored=False,
            replication_attempted=False,
            replication_success=False,
            replicated_restoration=False,
            false_repair=False,
        )

    mechanism_correct = diagnosis.mechanism == source_world.spec.causal_mechanism
    bridge_correct = (
        (relevance == "self_relevant" and diagnosis.kind == "bridge" and mechanism_correct)
        or (relevance == "neutral" and diagnosis.kind == "no_bridge")
    )
    repair_attempted = False
    repair_correct = False
    replication_attempted = False
    replication_success = False

    decision_world = _decision_world_at_observation(
        seed,
        relevance,
        budget,
        shift,
        actions,
        side_effects,
        diagnosis_position,
    )
    if diagnosis.kind == "bridge":
        passed, _, _ = decision_world.validate_bridge(diagnosis.mechanism, diagnosis.intervention)
        accepted_validation_passed = accepted_validation_passed and passed
        if passed:
            repair_attempted = True
            repair_correct, _, _ = _need_blind_repair(
                decision_world,
                diagnosis,
                diagnosis_self_prob or [0.0] * N_INTERNAL,
            )
            if repair_correct:
                replication = decision_world.replication_test(diagnosis.intervention)
                replication_attempted = replication.attempted
                replication_success = replication.success

    core_values = [decision_world.internal[i] for i in decision_world.spec.core_indices]
    organization_restored = repair_correct and min(core_values) >= 0.55
    replicated_restoration = organization_restored and replication_success
    false_repair = relevance == "neutral" and repair_attempted

    return CommonDecoderResult(
        exact_replay_match=exact,
        replayed_observations=len(replayed),
        diagnosis_made=True,
        diagnosis_kind=diagnosis.kind,
        diagnosis_observations=diagnosis_index,
        mechanism_correct=mechanism_correct,
        bridge_correct=bridge_correct,
        validation_attempted=any_validation_attempted,
        validation_passed=accepted_validation_passed,
        repair_attempted=repair_attempted,
        repair_correct=repair_correct,
        organization_restored=organization_restored,
        replication_attempted=replication_attempted,
        replication_success=replication_success,
        replicated_restoration=replicated_restoration,
        false_repair=false_repair,
    )
