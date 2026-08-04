from constitutive_inquiry.environment import Action, UnlabeledSelfWorld, isolating_bits
from constitutive_inquiry.model import InquiryModel


def calibrated_model(world):
    model = InquiryModel()
    mechanism = world.spec.causal_mechanism
    bits = isolating_bits(mechanism)
    for _ in range(4):
        model.update(world.observe(Action("self", bits, low_dose=True)))
    for primitive in world.available_primitives:
        model.update(world.observe(Action("self", bits, intervention=(primitive,), low_dose=True)))
    for a in world.available_primitives:
        for b in world.available_primitives:
            model.update(world.observe(Action("self", bits, intervention=(a, b), low_dose=True)))
    return model


def test_relational_matrix_is_complete():
    world = UnlabeledSelfWorld(7010, "self_relevant", observation_budget=100, grammar_family="branch_comp", core_size=5, primitive_cardinality=5)
    model = calibrated_model(world)
    matrix = model.relational_matrix(world.spec.causal_mechanism, world.available_primitives)
    assert len(matrix) == 25
    assert all(value == value for value in matrix.values())


def test_sequence_keys_preserve_order():
    world = UnlabeledSelfWorld(7003, "self_relevant", grammar_family="branch_comp", core_size=5, primitive_cardinality=5)
    model = InquiryModel()
    mechanism = world.spec.causal_mechanism
    bits = isolating_bits(mechanism)
    p0, p1 = world.available_primitives[:2]
    for seq in [(p0, p1), (p1, p0)]:
        model.update(world.observe(Action("self", bits, sense_indices=tuple(range(14)), intervention=seq, low_dose=True)))
    assert (mechanism, (p0, p1)) in model.external_stats
    assert (mechanism, (p1, p0)) in model.external_stats
