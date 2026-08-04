from constitutive_inquiry.agent import InquiryAgent
from constitutive_inquiry.environment import UnlabeledSelfWorld


def test_agent_uses_dynamic_operation_set():
    world = UnlabeledSelfWorld(7300, "self_relevant", observation_budget=90, grammar_family="branch_comp", core_size=5, primitive_cardinality=5)
    agent = InquiryAgent("reset_actual_generation", 7300, "test")
    records = agent.run(world)
    assert records[-1].primitive_cardinality == 5
    assert records[-1].search_space_fraction < 0.5


def test_confidence_mode_reserves_local_beam():
    from constitutive_inquiry.crossworld import CrossWorldMemory
    world = UnlabeledSelfWorld(7402, "self_relevant", observation_budget=180, grammar_family="branch_comp", core_size=5, primitive_cardinality=5)
    memory = CrossWorldMemory.load("results/training/relational_memory.json")
    agent = InquiryAgent("confidence_gated_relational_generation", 7402, "test", crossworld_memory=memory)
    records = agent.run(world)
    assert records[-1].local_beam_reserved
