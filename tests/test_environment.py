from constitutive_inquiry.environment import (
    Action, FAMILY_ROLE_PROGRAMS, ROLE_SINGLETON_EFFECT, UnlabeledSelfWorld,
    intervention_space_size, isolating_bits,
)


def test_program_is_order_sensitive():
    world = UnlabeledSelfWorld(7001, "self_relevant", grammar_family="context_comp", core_size=5, primitive_cardinality=7)
    program = world.spec.intervention_program
    reverse = tuple(reversed(program))
    assert world.intervention_strength(world.spec.causal_mechanism, program) >= 0.78
    if reverse != program:
        assert world.intervention_strength(world.spec.causal_mechanism, reverse) < world.intervention_strength(world.spec.causal_mechanism, program)


def test_singleton_roles_overlap():
    assert ROLE_SINGLETON_EFFECT["A"] == ROLE_SINGLETON_EFFECT["B"]
    assert ROLE_SINGLETON_EFFECT["C"] == ROLE_SINGLETON_EFFECT["D"]
    assert ROLE_SINGLETON_EFFECT["E"] == ROLE_SINGLETON_EFFECT["F"]


def test_cardinality_adds_and_removes_irrelevant_operations():
    missing = UnlabeledSelfWorld(7002, "self_relevant", grammar_family="branch_comp", core_size=5, primitive_cardinality=5)
    novel = UnlabeledSelfWorld(7003, "self_relevant", grammar_family="context_comp", core_size=5, primitive_cardinality=7)
    assert len(missing.available_primitives) == 5
    assert "F" not in missing.active_roles
    assert len(novel.available_primitives) == 7
    assert "X" in novel.active_roles


def test_label_permutation_preserves_role_program():
    fixed = UnlabeledSelfWorld(7002, "self_relevant", grammar_family="branch_comp", core_size=5, permute_labels=False, primitive_cardinality=5)
    permuted = UnlabeledSelfWorld(7002, "self_relevant", grammar_family="branch_comp", core_size=5, permute_labels=True, primitive_cardinality=5)
    assert fixed.spec.role_program == permuted.spec.role_program == FAMILY_ROLE_PROGRAMS["branch_comp"]
    assert fixed.spec.intervention_program != permuted.spec.intervention_program


def test_dynamic_sequence_space():
    assert intervention_space_size(4, 5) == 780
    assert intervention_space_size(4, 7) == 2800


def test_low_dose_calibration_is_accepted():
    world = UnlabeledSelfWorld(7000, "self_relevant", grammar_family="repeat", core_size=4)
    primitive = world.available_primitives[0]
    obs = world.observe(Action("self", isolating_bits(world.spec.causal_mechanism), intervention=(primitive,), low_dose=True))
    assert obs.intervention == (primitive,)


def test_nonstationary_world_changes_relational_law_but_keeps_program_functional():
    stable = UnlabeledSelfWorld(7403, "self_relevant", grammar_family="context_comp", core_size=6, primitive_cardinality=7, nonstationary=False)
    shifted = UnlabeledSelfWorld(7403, "self_relevant", grammar_family="context_comp", core_size=6, primitive_cardinality=7, nonstationary=True)
    pair = next(iter(stable.role_pair_effect))
    assert any(stable.role_pair_effect[k] != shifted.role_pair_effect[k] for k in stable.role_pair_effect)
    assert shifted.intervention_is_functional(shifted.spec.causal_mechanism, shifted.spec.intervention_program)


def test_fixed_memory_capacity_reference_decouples_execution_horizon():
    short = UnlabeledSelfWorld(7004, "self_relevant", observation_budget=360, memory_capacity_budget=320, grammar_family="branch_comp", core_size=5, primitive_cardinality=5)
    long = UnlabeledSelfWorld(7004, "self_relevant", observation_budget=380, memory_capacity_budget=320, grammar_family="branch_comp", core_size=5, primitive_cardinality=5)
    assert short.memory_capacity() == long.memory_capacity()
