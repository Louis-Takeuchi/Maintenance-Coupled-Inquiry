from constitutive_inquiry.crossworld import CrossWorldMemory
from constitutive_inquiry.environment import UnlabeledSelfWorld
from test_model import calibrated_model


def test_relational_alignment_survives_label_permutation():
    first = UnlabeledSelfWorld(7100, "self_relevant", observation_budget=100, grammar_family="repeat", core_size=4, primitive_cardinality=6, permute_labels=True)
    second = UnlabeledSelfWorld(7101, "self_relevant", observation_budget=100, grammar_family="repeat", core_size=4, primitive_cardinality=6, permute_labels=True)
    memory = CrossWorldMemory(strategy="relational")
    model1 = calibrated_model(first)
    p2r1, _, _ = memory.align(model1, first.spec.causal_mechanism, first.available_primitives, initialize=True)
    model2 = calibrated_model(second)
    p2r2, _, cost = memory.align(model2, second.spec.causal_mechanism, second.available_primitives)
    assert cost < 0.15
    for role in ("A", "B", "C", "D", "E", "F"):
        assert p2r1[first.role_to_primitive[role]] == p2r2[second.role_to_primitive[role]]


def test_alignment_handles_missing_and_novel_operations():
    base_world = UnlabeledSelfWorld(7200, "self_relevant", observation_budget=100, grammar_family="repeat", core_size=4, primitive_cardinality=6)
    memory = CrossWorldMemory(strategy="relational")
    memory.align(calibrated_model(base_world), base_world.spec.causal_mechanism, base_world.available_primitives, initialize=True)
    for cardinality, seed, family in [(5, 7202, "branch_comp"), (7, 7203, "context_comp")]:
        world = UnlabeledSelfWorld(seed, "self_relevant", observation_budget=120, grammar_family=family, core_size=5, primitive_cardinality=cardinality)
        p2r, _, cost = memory.align(calibrated_model(world), world.spec.causal_mechanism, world.available_primitives)
        assert len(p2r) == min(6, cardinality)
        assert cost < 0.15


def test_memory_decay_requires_refresh():
    memory = CrossWorldMemory()
    memory.successes = 4
    memory.worlds_seen = 4
    memory.template_weights[(0, 1, 0)] = 4.0
    before = memory.energy
    for _ in range(5):
        memory.maintain(success=None)
    assert memory.energy < before
    assert memory.template_weights[(0, 1, 0)] < 4.0


def test_memory_round_trip(tmp_path):
    memory = CrossWorldMemory()
    memory.template_weights[(0, 1)] = 2.0
    memory.successes = 2
    path = tmp_path / "memory.json"
    memory.save(path)
    loaded = CrossWorldMemory.load(path)
    assert loaded.template_weights == memory.template_weights
    assert loaded.successes == 2


def test_alignment_posterior_is_normalized():
    base = UnlabeledSelfWorld(7400, "self_relevant", observation_budget=120, grammar_family="repeat", core_size=4, primitive_cardinality=6)
    memory = CrossWorldMemory(strategy="relational")
    memory.align(calibrated_model(base), base.spec.causal_mechanism, base.available_primitives, initialize=True)
    target = UnlabeledSelfWorld(7401, "self_relevant", observation_budget=120, grammar_family="context_comp", core_size=6, primitive_cardinality=7)
    hypotheses = memory.alignment_posterior(calibrated_model(target), target.spec.causal_mechanism, target.available_primitives)
    assert hypotheses
    assert abs(sum(row.posterior for row in hypotheses) - 1.0) < 1e-9
    assert all(0.0 <= row.support <= 1.0 for row in hypotheses)


def test_quarantine_survives_rollback():
    memory = CrossWorldMemory()
    memory.template_weights[(0, 1, 2)] = 2.0
    checkpoint = memory.clone()
    memory.quarantine((0, 1, 2), "branch_comp")
    memory.template_weights[(0, 1, 2)] = 9.0
    memory.restore_from(checkpoint, preserve_quarantine=True)
    assert memory.template_weights[(0, 1, 2)] == 2.0
    assert memory.is_quarantined((0, 1, 2), "branch_comp")


def test_mapping_trust_penalizes_ambiguous_posterior(monkeypatch):
    memory = CrossWorldMemory()
    memory.energy = 1.0
    from constitutive_inquiry.crossworld import AlignmentHypothesis
    hypothesis = AlignmentHypothesis({'p0': 0}, {0: 'p0'}, 0.0, 0.0, 1.0)
    monkeypatch.setattr(memory, 'alignment_posterior', lambda *args, **kwargs: (hypothesis,))
    memory.last_alignment_entropy = 0.95
    low = memory.mapping_trust(None, 'm0', ('p0',))
    memory.last_alignment_entropy = 0.05
    high = memory.mapping_trust(None, 'm0', ('p0',))
    assert low < high
    assert low < 0.1


def test_restore_preserves_quarantine():
    memory = CrossWorldMemory()
    checkpoint = memory.clone()
    memory.quarantine((1, 2, 3), 'branch_comp')
    memory.restore_from(checkpoint, preserve_quarantine=True)
    assert memory.is_quarantined((1, 2, 3), 'branch_comp')
