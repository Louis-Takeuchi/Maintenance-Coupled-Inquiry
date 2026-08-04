from constitutive_inquiry.agent import InquiryAgent
from constitutive_inquiry.environment import UnlabeledSelfWorld


def test_causal_self_model_recovers_some_core():
    world = UnlabeledSelfWorld(11, "self_relevant", observation_budget=60, shift_observation=28, core_size=4, grammar_family="repeat")
    agent = InquiryAgent("reset_actual_generation", 11, "development")
    records = agent.run(world)
    assert records[27].core_recall >= 0.50
