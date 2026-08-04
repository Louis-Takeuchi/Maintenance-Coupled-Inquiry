from __future__ import annotations

from dataclasses import asdict, dataclass
import random

from .environment import (
    Action, FULL_SEQUENCE_SPACE, MAX_PROGRAM_LENGTH, MECHANISMS, N_INTERNAL, PRIMITIVES,
    UnlabeledSelfWorld, all_bits, isolating_bits, trigger,
)
from .model import Diagnosis, InquiryModel
from .crossworld import CrossWorldMemory
from .self_model import SelfModelLearner

MODES = (
    "confidence_gated_relational_generation",
    "ungated_relational_generation",
    "reset_actual_generation",
    "sparse_reset_generation",
    "posterior_no_quarantine_generation",
    "quarantine_no_local_reservation_generation",
    "frozen_correct_memory_generation",
    "adversarial_wrong_memory_generation",
    "oracle_family_generation",
    "no_null_confidence_gated_generation",
)

CONFIDENCE_MODES = {
    "confidence_gated_relational_generation",
    "posterior_no_quarantine_generation",
    "quarantine_no_local_reservation_generation",
    "frozen_correct_memory_generation",
    "adversarial_wrong_memory_generation",
    "no_null_confidence_gated_generation",
    "sparse_reset_generation",
}


@dataclass(frozen=True)
class StepRecord:
    split: str
    seed: int
    relevance: str
    mode: str
    observation_index: int
    domain: str
    bits: str
    probe_index: int
    sense_indices: str
    intervention: str
    intervention_length: int
    residual: int
    external_intensity: float
    intervention_risk: float
    need_total: float
    target_self_share: float
    predicted_core: str
    core_recall: float
    discovery_stage: str
    search_depth: int
    unique_sequences_evaluated: int
    search_space_fraction: float
    proposed_mechanism: str
    proposed_intervention: str
    exact_program: bool
    functional_program: bool
    diagnosis_made: bool
    diagnosis_kind: str
    diagnosis_target: int
    mechanism_correct: bool
    bridge_correct: bool
    suppression: float
    bridge_effect: float
    evidence_rows: int
    tested_scope: str
    validation_attempted: bool
    validation_passed: bool
    validation_effect: float
    repair_attempted: bool
    repair_correct: bool
    repair_improvement: float
    replication_attempted: bool
    replication_success: bool
    replication_blocked_fraction: float
    failed_repairs: int
    internal_min_core: float
    internal_mean_core: float
    total_cost: float
    alive: bool
    crossworld_successes: int
    crossworld_templates: int
    macro_reuse: bool
    primitive_cardinality: int
    relational_alignment_cost: float
    memory_energy: float
    memory_strategy: str
    alignment_entropy: float
    alignment_support: float
    mapping_trust: float
    memory_proposal_tested: bool
    memory_changed_action: bool
    wrong_memory_detected_before_repair: bool
    local_beam_reserved: bool
    quarantined_count: int


class InquiryAgent:
    def __init__(
        self,
        mode: str,
        seed: int,
        split: str,
        yoked_trace: list[list[float]] | None = None,
        crossworld_memory: CrossWorldMemory | None = None,
    ) -> None:
        if mode not in MODES:
            raise ValueError(mode)
        self.mode = mode
        self.seed = seed
        self.split = split
        self.rng = random.Random(seed + 710_111)
        strategy = "correlation" if mode.startswith("correlation") else "causal"
        self.self_model = SelfModelLearner(strategy)
        self.model = InquiryModel(allow_null=not mode.startswith("no_null"))
        self.observational = mode.startswith("observational")
        self.yoked_trace = yoked_trace or [[0.0] * N_INTERNAL]
        self.crossworld_memory = crossworld_memory
        self.use_memory = crossworld_memory is not None and not mode.startswith("reset") and not mode.startswith("oracle")
        self.use_macros = self.use_memory and "macro_disabled" not in mode
        self.use_transition_prior = self.use_macros
        self.records: list[StepRecord] = []
        self.action_history: list[Action] = []
        self.need_history: list[list[float]] = []
        self.sensing_panel: tuple[int, ...] = ()
        self.repaired = False
        self.replication_success = False
        self.replication_blocked_fraction = 0.0
        self.candidate_interventions: dict[str, tuple[str, ...]] = {}
        self.search_queue: list[tuple[str, tuple[str, ...]]] = []
        self.search_depth = 1
        self.search_complete = False
        # Within-world search hyperparameters are identical across memory controls.
        self.beam_width = 4
        self.expansions_per_mechanism = 7
        self.macro_reuse_ever = False
        self._macro_reuse_cache: dict[tuple[str, tuple[str, ...]], bool] = {}
        self.memory_sequences: set[tuple[str, tuple[str, ...]]] = set()
        self.memory_proposal_tested = False
        self.memory_changed_action = False
        self.wrong_memory_detected_before_repair = False
        self.local_beam_reserved = False
        self.mapping_trust = 0.0
        self.current_family = ""

    def run(self, world: UnlabeledSelfWorld) -> list[StepRecord]:
        while not world.done:
            needs = self._needs(world, world.observation_count)
            self.need_history.append(list(needs))
            action, target_share, stage = self._select_action(world, needs)
            obs = world.observe(action)
            self.action_history.append(action)
            self.self_model.update(obs)
            self.model.update(obs)

            self_prob = self._self_prob(world)
            diagnosis = self.model.diagnose(
                self_prob, self.candidate_interventions,
                force_positive=self.mode.startswith("no_null"),
                observational=self.observational,
            )
            validation_attempted = False
            validation_passed = False
            validation_effect = 0.0
            repair_attempted = False
            repair_correct = False
            repair_improvement = 0.0
            replication_attempted = False
            if diagnosis is not None and diagnosis.kind == "bridge" and not self.repaired:
                validation_attempted = True
                validation_passed, validation_effect, _ = world.validate_bridge(diagnosis.mechanism, diagnosis.intervention)
                if self.mode.startswith("no_null"):
                    validation_passed = True
                if validation_passed:
                    repair_attempted = True
                    repair_correct, repair_improvement = self._apply_repair(world, diagnosis, self_prob, needs)
                    self.repaired = repair_correct
                    self.model.register_repair_outcome(diagnosis, repair_correct, repair_improvement)
                    if repair_correct and not self.mode.startswith("no_replication"):
                        replication = world.replication_test(diagnosis.intervention)
                        replication_attempted = replication.attempted
                        self.replication_success = replication.success
                        self.replication_blocked_fraction = replication.blocked_fraction
                else:
                    memory_candidate = (diagnosis.mechanism, tuple(diagnosis.intervention)) in self.memory_sequences
                    if memory_candidate:
                        self.wrong_memory_detected_before_repair = True
                        if (
                            self.crossworld_memory is not None
                            and self.mode in {
                                "confidence_gated_relational_generation",
                                "quarantine_no_local_reservation_generation",
                                "adversarial_wrong_memory_generation",
                                "no_null_confidence_gated_generation",
                            }
                        ):
                            p2r, _, _ = self.crossworld_memory.align(
                                self.model, diagnosis.mechanism, world.available_primitives
                            )
                            sequence = tuple(diagnosis.intervention)
                            if sequence and all(p in p2r for p in sequence):
                                template = tuple(p2r[p] for p in sequence)
                                self.crossworld_memory.quarantine(template, world.spec.grammar_family)
                    self.model.register_validation_failure(diagnosis)
                    diagnosis = None

            predicted = self._predicted_core(world)
            true_core = set(world.spec.core_indices)
            recall = len(set(predicted) & true_core) / len(true_core)
            core_values = [world.internal[i] for i in world.spec.core_indices]
            selected_mechanism = diagnosis.mechanism if diagnosis else self._best_proposed_mechanism()
            selected_intervention = diagnosis.intervention if diagnosis else self.candidate_interventions.get(selected_mechanism, ())
            macro_reuse = False
            if selected_intervention and self.use_macros and self.crossworld_memory is not None:
                cache_key = (selected_mechanism, tuple(selected_intervention))
                if cache_key not in self._macro_reuse_cache:
                    self._macro_reuse_cache[cache_key] = self.crossworld_memory.is_macro_reuse(
                        self.model, selected_mechanism, tuple(selected_intervention), world.available_primitives
                    )
                macro_reuse = self._macro_reuse_cache[cache_key]
            self.macro_reuse_ever = self.macro_reuse_ever or macro_reuse
            unique_tested = len({a.intervention for a in self.action_history if a.intervention})
            self.records.append(StepRecord(
                split=self.split,
                seed=self.seed,
                relevance=world.relevance,
                mode=self.mode,
                observation_index=obs.index,
                domain=action.domain,
                bits="".join(map(str, action.bits)),
                probe_index=action.probe_index,
                sense_indices=",".join(map(str, action.sense_indices)),
                intervention=">".join(action.intervention),
                intervention_length=len(action.intervention),
                residual=obs.residual,
                external_intensity=obs.external_intensity,
                intervention_risk=obs.intervention_risk,
                need_total=sum(needs),
                target_self_share=target_share,
                predicted_core=",".join(map(str, predicted)),
                core_recall=recall,
                discovery_stage=stage,
                search_depth=self.search_depth,
                unique_sequences_evaluated=unique_tested,
                search_space_fraction=unique_tested / max(1, world.intervention_space_size()),
                proposed_mechanism=selected_mechanism,
                proposed_intervention=">".join(selected_intervention),
                exact_program=bool(selected_mechanism == world.spec.causal_mechanism and tuple(selected_intervention) == world.spec.intervention_program),
                functional_program=bool(selected_mechanism == world.spec.causal_mechanism and world.intervention_is_functional(selected_mechanism, selected_intervention)),
                diagnosis_made=diagnosis is not None,
                diagnosis_kind=diagnosis.kind if diagnosis else "",
                diagnosis_target=diagnosis.target_index if diagnosis else -1,
                mechanism_correct=bool(diagnosis and diagnosis.mechanism == world.spec.causal_mechanism),
                bridge_correct=bool(diagnosis and ((world.relevance == "self_relevant" and diagnosis.kind == "bridge" and diagnosis.mechanism == world.spec.causal_mechanism) or (world.relevance == "neutral" and diagnosis.kind == "no_bridge"))),
                suppression=diagnosis.suppression if diagnosis else 0.0,
                bridge_effect=diagnosis.bridge_effect if diagnosis else 0.0,
                evidence_rows=diagnosis.evidence_rows if diagnosis else 0,
                tested_scope=diagnosis.tested_scope if diagnosis else "",
                validation_attempted=validation_attempted,
                validation_passed=validation_passed,
                validation_effect=validation_effect,
                repair_attempted=repair_attempted,
                repair_correct=repair_correct,
                repair_improvement=repair_improvement,
                replication_attempted=replication_attempted,
                replication_success=self.replication_success,
                replication_blocked_fraction=self.replication_blocked_fraction,
                failed_repairs=self.model.failed_repairs,
                internal_min_core=min(core_values),
                internal_mean_core=sum(core_values) / len(core_values),
                total_cost=world.total_cost,
                alive=world.alive,
                crossworld_successes=self.crossworld_memory.successes if self.crossworld_memory else 0,
                crossworld_templates=len(self.crossworld_memory.template_counts) if self.crossworld_memory else 0,
                macro_reuse=self.macro_reuse_ever,
                primitive_cardinality=len(world.available_primitives),
                relational_alignment_cost=(
                    self.crossworld_memory.last_alignment_cost
                    if self.crossworld_memory is not None and self.crossworld_memory.prototype_matrix else 0.0
                ),
                memory_energy=self.crossworld_memory.energy if self.crossworld_memory is not None else 0.0,
                memory_strategy=self.crossworld_memory.strategy if self.crossworld_memory is not None else "none",
                alignment_entropy=self.crossworld_memory.last_alignment_entropy if self.crossworld_memory is not None else 0.0,
                alignment_support=self.crossworld_memory.last_alignment_support if self.crossworld_memory is not None else 0.0,
                mapping_trust=self.mapping_trust,
                memory_proposal_tested=self.memory_proposal_tested,
                memory_changed_action=self.memory_changed_action,
                wrong_memory_detected_before_repair=self.wrong_memory_detected_before_repair,
                local_beam_reserved=self.local_beam_reserved,
                quarantined_count=len(self.crossworld_memory.quarantined_pairs) if self.crossworld_memory is not None else 0,
            ))
        return self.records

    def _self_prob(self, world: UnlabeledSelfWorld) -> list[float]:
        if self.mode.startswith("oracle"):
            return [1.0 if i in world.spec.core_indices else 0.0 for i in range(N_INTERNAL)]
        return self.self_model.core_probabilities

    def _predicted_core(self, world: UnlabeledSelfWorld) -> tuple[int, ...]:
        return tuple(sorted(world.spec.core_indices)) if self.mode.startswith("oracle") else self.self_model.predicted_core()

    def _needs(self, world: UnlabeledSelfWorld, index: int) -> list[float]:
        if self.mode.startswith("curiosity"):
            return [0.0] * N_INTERNAL
        if self.mode.startswith("oracle"):
            return [max(0.0, 0.925 - world.internal[i]) / 0.30 if i in world.spec.core_indices else 0.0 for i in range(N_INTERNAL)]
        actual = self.self_model.need_vector()
        return self.yoked_trace[index % len(self.yoked_trace)] if "yoked" in self.mode else actual

    def _select_action(self, world: UnlabeledSelfWorld, needs: list[float]) -> tuple[Action, float, str]:
        index = world.observation_count
        if index < world.shift_observation:
            domain = "self" if index % 2 == 0 else "neutral"
            return Action(domain, all_bits()[index % len(all_bits())], self.self_model.probe_priority()), 0.5, "self_boundary_learning"

        topology_aware = not self.mode.startswith("no_topology")
        self.sensing_panel = self.self_model.sensing_priority(needs, 9, topology_aware)
        need = sum(needs)
        target_share = 0.50 if self.mode.startswith("curiosity") else (0.54 if need < 0.02 else min(0.86, 0.66 + 1.25 * need))
        domain = self._allocate_domain(world.shift_observation, target_share)
        if domain == "neutral":
            bits = all_bits()[(index * 7 + self.seed) % len(all_bits())]
            return Action("neutral", bits, sense_indices=self.sensing_panel[:4]), target_share, "neutral_control"
        action, stage = self._self_scientific_action(world)
        return action, target_share, stage

    def _self_scientific_action(self, world: UnlabeledSelfWorld) -> tuple[Action, str]:
        self.current_family = world.spec.grammar_family
        post_self = sum(1 for action in self.action_history[world.shift_observation:] if action.domain == "self")
        senses = self.sensing_panel
        if self.observational:
            mechanism = MECHANISMS[post_self % len(MECHANISMS)]
            bits = isolating_bits(mechanism) if post_self % 2 == 0 else self._global_control_bits()
            return Action("self", bits, sense_indices=senses), "observational"

        if post_self < 12:
            mechanism = MECHANISMS[(post_self // 3) % len(MECHANISMS)]
            return Action("self", isolating_bits(mechanism), sense_indices=senses), "mechanism_survey"

        active = self.model.active_mechanisms(2)
        if self.mode.startswith("oracle"):
            self.candidate_interventions[world.spec.causal_mechanism] = world.spec.intervention_program
            other = active[0] if active[0] != world.spec.causal_mechanism else active[-1]
            self.candidate_interventions[other] = world.mechanism_programs[other]
            return self._bridge_cycle_action(post_self - 12, active), "oracle_bridge_test"

        primitives = world.available_primitives
        singleton_len = 2 * len(primitives) * len(active)
        if post_self < 12 + singleton_len:
            offset = post_self - 12
            mechanism = active[(offset // (2 * len(primitives))) % len(active)]
            primitive = primitives[(offset // 2) % len(primitives)]
            return Action("self", isolating_bits(mechanism), sense_indices=senses, intervention=(primitive,), low_dose=True), "ambiguous_singleton_calibration"

        # Directed pair calibration identifies operation roles through relations rather
        # than scalar singleton ranks. The graph is measured on the strongest mechanism.
        calibration_pairs = self._relational_calibration_pairs(primitives)
        relation_len = len(calibration_pairs)
        if post_self < 12 + singleton_len + relation_len:
            offset = post_self - 12 - singleton_len
            mechanism = active[0]
            a, b = calibration_pairs[offset]
            return Action("self", isolating_bits(mechanism), sense_indices=senses, intervention=(a, b), low_dose=True), "relational_role_calibration"

        # Stop intervention search as soon as each active mechanism has a strongly
        # suppressive tested program. Memory conditions reach this point earlier when a
        # transferred relational macro is correct.
        strong_candidates: dict[str, tuple[str, ...]] = {}
        should_check_early_stop = bool(
            not self.search_complete
            and self.action_history
            and len(self.action_history[-1].intervention) >= 3
        )
        if should_check_early_stop:
            for mechanism in active:
                ranked_now = self.model.ranked_sequences(mechanism)
                if ranked_now:
                    top = ranked_now[0]
                    suppression, _, treated = self.model.candidate_suppression(mechanism, top)
                    memory_candidate = (mechanism, tuple(top)) in self.memory_sequences
                    gate_ok = True
                    if self.mode in CONFIDENCE_MODES and memory_candidate:
                        # A transferred complete program may stop search only when the
                        # mapping is independently supported or repeated current-world
                        # intervention evidence is already strong.
                        gate_ok = self.mapping_trust >= 0.06 or (treated >= 2 and suppression >= 0.75)
                    if len(top) >= 3 and treated >= 1 and suppression >= 0.70 and gate_ok:
                        strong_candidates[mechanism] = top
            if len(strong_candidates) == len(active):
                self.candidate_interventions.update(strong_candidates)
                self.search_complete = True

        if self.mode.startswith("greedy"):
            for mechanism in active:
                ranked = self.model.ranked_sequences(mechanism, 1)
                self.candidate_interventions[mechanism] = ranked[0] if ranked else ()
            return self._bridge_cycle_action(post_self - 12 - singleton_len - relation_len, active), "greedy_bridge_test"

        max_depth = 2 if self.mode.startswith("pair_limited") else MAX_PROGRAM_LENGTH
        if not self.search_complete:
            # Pair calibration has already evaluated every length-two program. Skip
            # exhausted depths until a genuinely new queue is produced.
            while not self.search_queue and not self.search_complete:
                self._prepare_search_depth(active, max_depth, world)
            if self.search_queue:
                mechanism, sequence = self.search_queue.pop(0)
                return Action("self", isolating_bits(mechanism), sense_indices=senses, intervention=sequence), "beam_grammar_search"

        if not self.candidate_interventions:
            for mechanism in active:
                ranked = self.model.ranked_sequences(mechanism)
                self.candidate_interventions[mechanism] = ranked[0] if ranked else ()
        bridge_offset = max(0, post_self - 12 - singleton_len - relation_len)
        return self._bridge_cycle_action(bridge_offset, active), "bridge_test"

    def _relational_calibration_pairs(self, primitives: tuple[str, ...]) -> list[tuple[str, str]]:
        if self.mode not in CONFIDENCE_MODES:
            return [(a, b) for a in primitives for b in primitives]
        # Sparse, label-invariant coverage: diagonal plus two directed cyclic offsets.
        # This leaves enough disjoint pair evidence for posterior fit and validation,
        # while allowing trusted memory to reduce current-world inquiry cost.
        n = len(primitives)
        pairs: list[tuple[str, str]] = []
        for i, a in enumerate(primitives):
            for step in (0, 1, 2):
                pair = (a, primitives[(i + step) % n])
                if pair not in pairs:
                    pairs.append(pair)
        return pairs

    def _prepare_search_depth(self, active: tuple[str, ...], max_depth: int, world: UnlabeledSelfWorld) -> None:
        if self.search_depth == 1:
            self.search_depth = 2
        if self.search_depth > max_depth:
            for mechanism in active:
                ranked = self.model.ranked_sequences(mechanism)
                self.candidate_interventions[mechanism] = ranked[0] if ranked else ()
            self.search_complete = True
            return

        queue: list[tuple[str, tuple[str, ...]]] = []
        for mechanism in active:
            existing = set(self.model.tested_sequences(mechanism))
            memory_proposals: list[tuple[str, ...]] = []
            memory_confidence: dict[tuple[str, ...], float] = {}
            if self.use_memory and self.crossworld_memory is not None:
                if self.mode in CONFIDENCE_MODES:
                    rows = self.crossworld_memory.posterior_proposals(
                        self.model, mechanism, self.search_depth, world.available_primitives,
                        family=world.spec.grammar_family, include_macros=self.use_macros,
                        limit=self.expansions_per_mechanism,
                    )
                    self.mapping_trust = max(
                        self.mapping_trust,
                        self.crossworld_memory.mapping_trust(self.model, mechanism, world.available_primitives),
                    )
                    # Final v0.14 gate: transferred memory is executable only when
                    # the alignment posterior is both concentrated and independently
                    # supported. A high-scoring best map is insufficient when several
                    # incompatible maps remain plausible.
                    gate_open = (
                        self.mapping_trust >= 0.06
                        and self.crossworld_memory.last_alignment_entropy <= 0.20
                        and self.crossworld_memory.last_alignment_support >= 0.70
                    )
                    if self.mode == "quarantine_no_local_reservation_generation":
                        # Ablation: use posterior proposals without a safe local-beam
                        # requirement even when alignment uncertainty is high.
                        gate_open = True
                    for sequence, confidence, _template in rows:
                        if gate_open and confidence >= 1e-6:
                            memory_proposals.append(sequence)
                            memory_confidence[sequence] = confidence
                else:
                    memory_proposals = self.crossworld_memory.proposals(
                        self.model, mechanism, self.search_depth, world.available_primitives,
                        include_macros=self.use_macros, limit=self.expansions_per_mechanism,
                    )

            ranked_parents = self.model.ranked_sequences(mechanism, self.search_depth - 1)
            if self.mode in CONFIDENCE_MODES and self.mode != "quarantine_no_local_reservation_generation":
                # A protected local beam is defined without transferred sequences.
                # This prevents an uncertain memory proposal from becoming the parent
                # of every later local expansion.
                parents = [
                    parent for parent in ranked_parents
                    if (mechanism, tuple(parent)) not in self.memory_sequences
                ][:self.beam_width]
            else:
                parents = ranked_parents[:self.beam_width]
            if not parents:
                parents = [(p,) for p in world.available_primitives[:self.beam_width]]

            # Memory proposals are tested early, but confidence-gated modes never let
            # them eliminate every locally generated competitor.
            fresh_memory = [sequence for sequence in memory_proposals if sequence not in existing]
            memory_slots = 3
            if self.mode in CONFIDENCE_MODES:
                # Test one posterior-supported transfer alternative at a time. Local
                # search is maintained in a separate reserved beam below.
                memory_slots = 1
                if self.mode == "quarantine_no_local_reservation_generation":
                    memory_slots = 5
            for sequence in fresh_memory[:memory_slots]:
                queue.append((mechanism, sequence))
                self.memory_sequences.add((mechanism, tuple(sequence)))
                self.memory_proposal_tested = True

            candidates: list[tuple[float, tuple[str, ...]]] = []
            best_parent = parents[0]
            guaranteed = [best_parent + (p,) for p in world.available_primitives]
            for sequence in guaranteed:
                if sequence not in existing:
                    candidates.append((10.0, sequence))
            for parent in parents[1:]:
                parent_suppression, _, _ = self.model.candidate_suppression(mechanism, parent)
                for primitive in world.available_primitives:
                    sequence = parent + (primitive,)
                    if sequence in existing:
                        continue
                    singleton_suppression, _, _ = self.model.candidate_suppression(mechanism, (primitive,))
                    memory_prior = 0.0
                    if (
                        self.use_transition_prior
                        and self.crossworld_memory is not None
                        and (self.mode not in CONFIDENCE_MODES or self.mode == "quarantine_no_local_reservation_generation")
                    ):
                        memory_prior = self.crossworld_memory.transition_prior(
                            self.model, mechanism, sequence, world.available_primitives
                        )
                    predicted = (
                        parent_suppression + 0.30 * singleton_suppression
                        + 0.45 * memory_prior
                        - 0.12 * world.intervention_risk(sequence) - 0.004 * len(sequence)
                    )
                    candidates.append((predicted, sequence))
            candidates.sort(key=lambda row: (row[0], row[1]), reverse=True)

            local_limit = self.expansions_per_mechanism
            if fresh_memory and self.mode in CONFIDENCE_MODES:
                # Unvalidated memory is additional to the complete local beam. Only a
                # remembered prefix that has already shown direct current-world
                # suppression may reduce later local expansion.
                validated_memory_parent = False
                for parent in ranked_parents:
                    if len(parent) != self.search_depth - 1:
                        continue
                    if (mechanism, tuple(parent)) not in self.memory_sequences:
                        continue
                    suppression, _, treated = self.model.candidate_suppression(mechanism, parent)
                    if treated >= 1 and suppression >= 0.55:
                        validated_memory_parent = True
                        break
                if validated_memory_parent:
                    local_limit = 4
            if self.mode == "quarantine_no_local_reservation_generation" and fresh_memory:
                local_limit = 2
            chosen: list[tuple[str, ...]] = []
            for _, sequence in candidates:
                if sequence not in chosen and sequence not in fresh_memory[:memory_slots]:
                    chosen.append(sequence)
                if len(chosen) >= local_limit:
                    break
            if chosen:
                self.local_beam_reserved = True
                queue.extend((mechanism, sequence) for sequence in chosen)

            if fresh_memory and chosen and fresh_memory[0] != chosen[0]:
                self.memory_changed_action = True

        self.search_queue = queue
        self.search_depth += 1

    def _bridge_cycle_action(self, offset: int, active: tuple[str, ...]) -> Action:
        mechanism = active[(offset // 4) % len(active)]
        phase = offset % 4
        intervention = self.candidate_interventions.get(mechanism, ())
        if phase == 0:
            return Action("self", isolating_bits(mechanism), sense_indices=self.sensing_panel)
        if phase == 1:
            return Action("self", self._global_control_bits(), sense_indices=self.sensing_panel)
        if phase == 2:
            return Action("self", isolating_bits(mechanism), sense_indices=self.sensing_panel, intervention=intervention)
        return Action("self", self._global_control_bits(), sense_indices=self.sensing_panel)

    def _allocate_domain(self, shift: int, target_self_share: float) -> str:
        post = self.action_history[shift:]
        self_count = sum(action.domain == "self" for action in post)
        return "self" if self_count < target_self_share * (len(post) + 1) else "neutral"

    @staticmethod
    def _global_control_bits() -> tuple[int, int, int, int]:
        return next(bits for bits in all_bits() if not any(trigger(m, bits) for m in MECHANISMS))

    def _best_proposed_mechanism(self) -> str:
        rates = self.model.mechanism_rates()
        return max(rates, key=rates.get)

    def _apply_repair(self, world: UnlabeledSelfWorld, diagnosis: Diagnosis, self_prob: list[float], needs: list[float]) -> tuple[bool, float]:
        priority = [0.45 * (i == diagnosis.target_index) + 0.35 * needs[i] + 0.20 * self_prob[i] for i in range(N_INTERNAL)]
        best_operator, best_score = next(iter(world.restore_targets)), -1e9
        for operator in world.restore_targets:
            probe = world.probe_restore(operator)
            score = sum(delta * weight for delta, weight in zip(probe.delta, priority))
            if score > best_score:
                best_operator, best_score = operator, score
        result = world.repair_sequence(diagnosis.intervention, best_operator)
        return result.correct, result.improvement


def record_to_dict(record: StepRecord) -> dict:
    return asdict(record)
