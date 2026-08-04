from constitutive_inquiry.agent import InquiryAgent
from constitutive_inquiry.protocol import get_condition
from constitutive_inquiry.replay import run_common_decoder_replay, source_evidence_prefix
from constitutive_inquiry.unified_experiment import make_world


def test_exact_replay_matches_source_evidence_prefix():
    budget = 80
    shift = 28
    world = make_world(0, "self_relevant", budget, shift)
    agent = InquiryAgent("sparse_reset_generation", 0, "test", condition=get_condition("actual_need"))
    agent.run(world)
    actions, expected, side_effects = source_evidence_prefix(agent)
    result = run_common_decoder_replay(0, "self_relevant", budget, shift, actions, expected, side_effects)
    assert result.exact_replay_match
    assert result.replayed_observations == len(actions)


def test_common_decoder_summary_includes_need_blind_repair_outcomes():
    budget = 80
    shift = 28
    world = make_world(0, "self_relevant", budget, shift)
    agent = InquiryAgent("sparse_reset_generation", 0, "test", condition=get_condition("actual_need"))
    agent.run(world)
    actions, expected, side_effects = source_evidence_prefix(agent)
    result = run_common_decoder_replay(0, "self_relevant", budget, shift, actions, expected, side_effects)
    fields = result.to_summary_fields()
    assert fields["replay_exact_match"] == 1
    assert "common_decoder_repair_correct" in fields
    assert "common_decoder_replicated_restoration" in fields
