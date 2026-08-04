from dataclasses import dataclass

from constitutive_inquiry.agent import InquiryAgent
from constitutive_inquiry.environment import N_INTERNAL, RepairProbe, RepairResult, UnlabeledSelfWorld
from constitutive_inquiry.model import Diagnosis
from constitutive_inquiry.protocol import NeedPolicy, get_condition
from constitutive_inquiry.unified_experiment import build_yoke_map, evaluation_world_config


def test_yoke_map_is_cross_seed_and_stratum_matched():
    mapping = build_yoke_map(range(40))
    assert set(mapping) == set(range(40))
    for focal, donor in mapping.items():
        assert donor != focal
        assert evaluation_world_config(focal).stratum() == evaluation_world_config(donor).stratum()


def test_primary_need_policies_are_explicit():
    actual = get_condition("actual_need")
    yoked = get_condition("yoked_need")
    curiosity = get_condition("curiosity")
    no_need = get_condition("no_need")
    assert actual.need_policy == NeedPolicy.ACTUAL
    assert yoked.need_policy == NeedPolicy.YOKED
    assert curiosity.need_policy == NeedPolicy.CURIOSITY
    assert no_need.need_policy == NeedPolicy.NONE
    assert all(condition.common_repair_decoder for condition in (actual, yoked, curiosity, no_need))


def test_need_generation_differs_by_condition():
    world = UnlabeledSelfWorld(0, "self_relevant", observation_budget=20, shift_observation=4, core_size=5, grammar_family="branch_comp", primitive_cardinality=5)
    actual = InquiryAgent("sparse_reset_generation", 0, "test", condition=get_condition("actual_need"))
    actual.self_model.baseline = [0.925] * N_INTERNAL
    actual.self_model.last_seen = [0.80] + [0.925] * (N_INTERNAL - 1)
    actual.self_model.core_probabilities = [1.0] + [0.0] * (N_INTERNAL - 1)
    assert actual._needs(world, 0)[0] > 0.0

    yoked_trace = [[0.0, 0.4] + [0.0] * (N_INTERNAL - 2)]
    yoked = InquiryAgent("sparse_reset_generation", 0, "test", yoked_trace=yoked_trace, condition=get_condition("yoked_need"))
    assert yoked._needs(world, 0) == yoked_trace[0]

    for condition_id in ("curiosity", "no_need"):
        agent = InquiryAgent("sparse_reset_generation", 0, "test", condition=get_condition(condition_id))
        assert agent._needs(world, 0) == [0.0] * N_INTERNAL


class _RepairWorld:
    def __init__(self):
        self.restore_targets = {"r0": 0, "r1": 1}
        self.chosen = None

    def probe_restore(self, operator: str) -> RepairProbe:
        delta = [0.0] * N_INTERNAL
        delta[0 if operator == "r0" else 1] = 1.0
        return RepairProbe(operator, tuple(delta), 0.0)

    def repair_sequence(self, intervention, operator):
        self.chosen = operator
        return RepairResult(tuple(intervention), operator, True, True, True, True, 0.0, 1.0)


def test_common_repair_decoder_is_need_blind():
    diagnosis = Diagnosis("bridge", "m0", 0, ("p0",), 1.0, 1.0, 1.0, 20, "test")
    self_prob = [0.7, 0.6] + [0.0] * (N_INTERNAL - 2)
    agent = InquiryAgent("sparse_reset_generation", 0, "test", condition=get_condition("actual_need"))
    first = _RepairWorld()
    agent._apply_repair(first, diagnosis, self_prob, [0.0, 100.0] + [0.0] * (N_INTERNAL - 2))
    second = _RepairWorld()
    agent._apply_repair(second, diagnosis, self_prob, [100.0, 0.0] + [0.0] * (N_INTERNAL - 2))
    assert first.chosen == second.chosen == "r0"


def test_ablation_flags_do_not_conflate_null_and_validation():
    no_null = InquiryAgent("sparse_reset_generation", 0, "test", condition=get_condition("no_null"))
    no_validation = InquiryAgent("sparse_reset_generation", 0, "test", condition=get_condition("no_bridge_validation"))
    assert no_null.force_positive
    assert no_null.validation_enabled
    assert not no_validation.force_positive
    assert not no_validation.validation_enabled


def test_yoked_component_permutation_is_deranged_and_preserves_totals():
    from constitutive_inquiry.unified_experiment import permute_yoked_trace, yoke_component_shift
    trace = [[float(i) for i in range(N_INTERNAL)], [float(i * 2) for i in range(N_INTERNAL)]]
    shifted = permute_yoked_trace(trace, 0, 6)
    assert 1 <= yoke_component_shift(0, 6) < N_INTERNAL
    assert all(sum(a) == sum(b) for a, b in zip(trace, shifted))
    assert all(a[i] != b[i] for a, b in zip(trace, shifted) for i in range(1, N_INTERNAL))


def test_combined_null_validation_ablation_is_explicit():
    combined = get_condition("no_null_no_validation")
    assert not combined.allow_null
    assert not combined.bridge_validation


def test_primary_sensing_policies_are_explicit_and_need_blind_controls_match():
    from constitutive_inquiry.protocol import SensingPolicy, UNIFIED_SENSING_COUNT
    assert UNIFIED_SENSING_COUNT == 2
    assert get_condition("actual_need").sensing_policy == SensingPolicy.NEED_GUIDED
    assert get_condition("yoked_need").sensing_policy == SensingPolicy.NEED_GUIDED
    assert get_condition("curiosity").sensing_policy == SensingPolicy.EPISTEMIC
    assert get_condition("no_need").sensing_policy == SensingPolicy.EPISTEMIC


def test_need_guided_sensing_tracks_component_while_epistemic_selector_is_need_blind():
    from constitutive_inquiry.self_model import SelfModelLearner

    learner = SelfModelLearner("causal")
    learner.core_probabilities = [0.5] * N_INTERNAL
    learner.last_seen_at = [0] * N_INTERNAL
    learner.states = [tuple([0.9] * N_INTERNAL)] * 12
    learner.probe_counts = [1] * N_INTERNAL

    epistemic_before = learner.epistemic_sensing_priority(count=2)
    needs = [0.0] * N_INTERNAL
    needs[11] = 1.0
    guided = learner.need_guided_sensing_priority(needs, count=2)
    epistemic_after = learner.epistemic_sensing_priority(count=2)

    assert epistemic_before == epistemic_after
    assert 11 in guided


def test_unified_candidate_budget_and_shift_are_frozen():
    from constitutive_inquiry.protocol import UNIFIED_OBSERVATION_BUDGET, UNIFIED_SHIFT_OBSERVATION
    assert UNIFIED_OBSERVATION_BUDGET == 600
    assert UNIFIED_SHIFT_OBSERVATION == 28


def test_endpoint_registry_uses_component_alignment_not_binary_domain_for_actual_vs_yoked():
    from constitutive_inquiry.protocol import ENDPOINTS

    target = ENDPOINTS["causal_target_sensing_share"]
    domain = ENDPOINTS["self_domain_observation_share"]
    assert target.role == "primary_mechanism"
    assert target.contrast == "actual_need - yoked_need"
    assert domain.role == "process_endpoint"
    assert "actual and yoked are not expected" in domain.interpretation
    assert ENDPOINTS["false_repair"].role == "mandatory_safety_gate"
    assert ENDPOINTS["false_repair"].contrast == "actual_need absolute rate"
    assert ENDPOINTS["replicated_restoration"].role == "confirmatory_secondary"
    assert ENDPOINTS["replicated_restoration"].initial_sesoi == "0.10 absolute probability difference"
    assert ENDPOINTS["explicit_no_bridge"].role == "supporting_safety"


def test_chunked_yoked_execution_accepts_frozen_cross_seed_map(tmp_path):
    from constitutive_inquiry.unified_experiment import run_unified_suite

    summaries, _ = run_unified_suite(
        tmp_path,
        seeds=[0],
        split="development",
        condition_ids=["yoked_need"],
        relevance_levels=["self_relevant"],
        yoke_map_override={0: 6},
        budget=2,
        shift=0,
    )
    assert len(summaries) == 1
    assert summaries[0]["yoke_donor_seed"] == 6
