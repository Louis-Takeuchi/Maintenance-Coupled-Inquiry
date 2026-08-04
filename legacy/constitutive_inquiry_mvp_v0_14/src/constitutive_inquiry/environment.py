from __future__ import annotations

from dataclasses import dataclass
import math
import random

DOMAINS = ("self", "neutral")
MECHANISMS = ("m0", "m1", "m2", "m3")
PRIMITIVES = tuple(f"p{i}" for i in range(8))
RELEVANCE_LEVELS = ("self_relevant", "neutral")
TOPOLOGIES = ("ring", "chain", "dense")
N_INTERNAL = 14
MAX_PROGRAM_LENGTH = 4
ROLES = ("A", "B", "C", "D", "E", "F")
DECOY_ROLES = ("X", "Y")
ALL_ROLES = ROLES + DECOY_ROLES
TRAIN_FAMILIES = ("repeat", "delayed", "inhibitor_first", "fork")
HELDOUT_FAMILIES = ("branch_comp", "context_comp")
GRAMMAR_FAMILIES = TRAIN_FAMILIES + HELDOUT_FAMILIES
FAMILY_ROLE_PROGRAMS = {
    "repeat": ("A", "B", "A"),
    "delayed": ("B", "A", "C"),
    "inhibitor_first": ("D", "A", "C"),
    "fork": ("E", "A", "B"),
    "branch_comp": ("A", "C", "B"),
    "context_comp": ("A", "B", "A", "C"),
}
# Singleton effects deliberately overlap. A/B, C/D, and E/F cannot be
# reliably aligned from scalar singleton suppression alone.
ROLE_SINGLETON_EFFECT = {
    "A": 0.082, "B": 0.082,
    "C": 0.058, "D": 0.058,
    "E": 0.034, "F": 0.034,
    "X": 0.050, "Y": 0.050,
}
# A label-invariant directed relational signature. Rows and columns jointly
# identify roles even when singleton effects overlap.
ROLE_PAIR_EFFECT = {
    (a, b): 0.012 + 0.011 * (((i + 1) * 3 + (j + 1) * 5 + i * j) % 9)
    for i, a in enumerate(ALL_ROLES)
    for j, b in enumerate(ALL_ROLES)
}
FULL_SEQUENCE_SPACE = sum(len(PRIMITIVES) ** k for k in range(1, MAX_PROGRAM_LENGTH + 1))


def base_rule(bits: tuple[int, int, int, int]) -> int:
    x0, x1, x2, x3 = bits
    return x0 ^ x1 ^ (x2 & x3)


def trigger(mechanism: str, bits: tuple[int, int, int, int]) -> int:
    x0, x1, x2, x3 = bits
    if mechanism == "m0":
        return int(x0 == 1 and x1 == 1)
    if mechanism == "m1":
        return int(x2 == 1 and x3 == 0)
    if mechanism == "m2":
        return int(x3 == 1 and x0 == 0)
    if mechanism == "m3":
        return int(x1 == 0 and x2 == 0)
    raise ValueError(mechanism)


def all_bits() -> tuple[tuple[int, int, int, int], ...]:
    return tuple((a, b, c, d) for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1))


def isolating_bits(mechanism: str) -> tuple[int, int, int, int]:
    candidates = [
        bits for bits in all_bits()
        if trigger(mechanism, bits)
        and sum(trigger(other, bits) for other in MECHANISMS if other != mechanism) == 0
    ]
    if not candidates:
        candidates = [bits for bits in all_bits() if trigger(mechanism, bits)]
    return candidates[0]


def intervention_space_size(max_length: int = MAX_PROGRAM_LENGTH, primitive_count: int | None = None) -> int:
    n = primitive_count or len(PRIMITIVES)
    return sum(n ** k for k in range(1, max_length + 1))


@dataclass(frozen=True)
class Action:
    domain: str
    bits: tuple[int, int, int, int]
    probe_index: int = -1
    sense_indices: tuple[int, ...] = ()
    intervention: tuple[str, ...] = ()
    low_dose: bool = False


@dataclass(frozen=True)
class Observation:
    index: int
    domain: str
    bits: tuple[int, int, int, int]
    outcome: int
    residual: int
    external_intensity: float
    noise_flip: bool
    active_mechanisms: tuple[str, ...]
    internal_before: tuple[float | None, ...]
    internal_after: tuple[float | None, ...]
    observed_indices: tuple[int, ...]
    pulse_index: int
    retained_capacity: int
    intervention: tuple[str, ...]
    intervention_strengths: tuple[float, ...]
    intervention_cost: float
    intervention_risk: float
    exposure_cost: float
    sensing_cost: float


@dataclass(frozen=True)
class RepairProbe:
    operator: str
    delta: tuple[float, ...]
    cost: float


@dataclass(frozen=True)
class RepairResult:
    intervention: tuple[str, ...]
    restore_operator: str
    intervention_correct: bool
    functionally_equivalent: bool
    target_correct: bool
    correct: bool
    cost: float
    improvement: float


@dataclass(frozen=True)
class ReplicationResult:
    attempted: bool
    success: bool
    blocked_fraction: float
    damage_avoided: float
    cost: float
    environment_shift: float


@dataclass(frozen=True)
class WorldSpec:
    seed: int
    relevance: str
    shift_observation: int
    self_mechanisms: tuple[str, str]
    causal_mechanism: str
    nuisance_mechanism: str
    neutral_mechanism: str
    core_indices: tuple[int, ...]
    core_size: int
    topology: str
    resource_index: int
    memory_index: int
    sensor_index: int
    mediator_index: int
    damaged_index: int
    readout_index: int
    passive_visible_indices: tuple[int, ...]
    intervention_program: tuple[str, ...]
    program_length: int
    restore_operator: str
    grammar_family: str
    role_program: tuple[str, ...]
    label_permuted: bool
    available_primitives: tuple[str, ...]
    active_roles: tuple[str, ...]
    nonstationary: bool


class UnlabeledSelfWorld:
    """Partially observed world with an order-sensitive intervention grammar.

    Each mechanism has a hidden primitive sequence. Prefixes provide graded external
    suppression, repeated tokens can matter, and some transitions carry side effects.
    Development worlds use length-two programs; evaluation worlds use unseen lengths
    three and four. The agent receives no program hint.
    """

    def __init__(
        self,
        seed: int,
        relevance: str,
        observation_budget: int = 260,
        shift_observation: int = 28,
        core_size: int = 4,
        topology: str | None = None,
        program_length: int | None = None,
        grammar_family: str | None = None,
        permute_labels: bool = True,
        primitive_cardinality: int | None = None,
        nonstationary: bool = False,
    ) -> None:
        if relevance not in RELEVANCE_LEVELS:
            raise ValueError(relevance)
        if not 3 <= core_size <= N_INTERNAL - 5:
            raise ValueError("invalid core_size")
        self.seed = seed
        self.relevance = relevance
        self.observation_budget = observation_budget
        self.shift_observation = shift_observation
        self.rng = random.Random(seed)
        self.core_size = core_size
        self.topology = topology or TOPOLOGIES[seed % len(TOPOLOGIES)]
        if self.topology not in TOPOLOGIES:
            raise ValueError(self.topology)
        if grammar_family is None:
            families = TRAIN_FAMILIES if seed < 1000 else HELDOUT_FAMILIES
            grammar_family = families[seed % len(families)]
        if grammar_family not in GRAMMAR_FAMILIES:
            raise ValueError(grammar_family)
        self.grammar_family = grammar_family
        self.role_program = FAMILY_ROLE_PROGRAMS[grammar_family]
        self.program_length = program_length or len(self.role_program)
        if self.program_length != len(self.role_program):
            raise ValueError("program_length must match grammar family")
        self.permute_labels = permute_labels
        # Training uses six semantic roles. Evaluation alternates a five-role world
        # (irrelevant role F missing) and a seven-operation world with one novel decoy X.
        if primitive_cardinality is None:
            primitive_cardinality = 6
        if primitive_cardinality not in (5, 6, 7):
            raise ValueError("primitive_cardinality must be 5, 6, or 7")
        active_roles = list(ROLES[: min(6, primitive_cardinality)])
        if primitive_cardinality == 7:
            active_roles.append("X")
        required = set(self.role_program)
        if not required.issubset(active_roles):
            raise ValueError(f"grammar requires missing roles: {sorted(required - set(active_roles))}")
        role_primitives = list(PRIMITIVES)
        if permute_labels:
            random.Random(seed * 73_919 + 401).shuffle(role_primitives)
        selected_primitives = tuple(role_primitives[:primitive_cardinality])
        self.active_roles = tuple(active_roles)
        self.available_primitives = selected_primitives
        self.role_to_primitive = dict(zip(self.active_roles, self.available_primitives))
        self.primitive_to_role = {primitive: role for role, primitive in self.role_to_primitive.items()}
        self.nonstationary = bool(nonstationary)
        self.role_pair_effect = dict(ROLE_PAIR_EFFECT)
        if self.nonstationary:
            perturb_rng = random.Random(seed + 14_140_014)
            for pair in list(self.role_pair_effect):
                a, b = pair
                if a in self.active_roles and b in self.active_roles and perturb_rng.random() < 0.28:
                    delta = perturb_rng.choice((-1.0, 1.0)) * perturb_rng.uniform(0.020, 0.045)
                    self.role_pair_effect[pair] = max(0.002, self.role_pair_effect[pair] + delta)

        indices = list(range(N_INTERNAL))
        self.rng.shuffle(indices)
        core = tuple(indices[:core_size])
        resource, memory, sensor = core[:3]
        noncore = indices[core_size:]
        readout = noncore[0]
        mediator = core[(seed + 1) % core_size]
        damaged = core[(seed + 2) % core_size]
        if damaged == mediator:
            damaged = core[(core.index(mediator) + 1) % core_size]

        mechs = list(MECHANISMS)
        self.rng.shuffle(mechs)
        causal, nuisance, neutral_mech = mechs[:3]
        self.self_mechanisms = (causal, nuisance)

        self.mechanism_programs: dict[str, tuple[str, ...]] = {}
        active_nonprogram = [r for r in self.active_roles if r not in self.role_program] or list(self.active_roles)
        for j, mechanism in enumerate(MECHANISMS):
            if mechanism in self.self_mechanisms:
                roles = self.role_program
            else:
                # Distractor programs preserve length but alter order or introduce an
                # available non-program role. They never require a missing primitive.
                replacement = active_nonprogram[j % len(active_nonprogram)]
                distractors = (
                    tuple(reversed(self.role_program)),
                    tuple(self.role_program[1:] + self.role_program[:1]),
                    tuple((replacement,) + self.role_program[1:]),
                    tuple(self.role_program[:-1] + (replacement,)),
                )
                roles = distractors[j % len(distractors)]
            self.mechanism_programs[mechanism] = tuple(self.role_to_primitive[r] for r in roles)

        self.position_effect = {
            (m, position, primitive): self.rng.uniform(0.001, 0.006)
            for m in MECHANISMS
            for position in range(MAX_PROGRAM_LENGTH)
            for primitive in self.available_primitives
        }
        for m, program in self.mechanism_programs.items():
            for position, primitive in enumerate(program):
                self.position_effect[(m, position, primitive)] = 0.072 + self.rng.uniform(-0.005, 0.005)

        self.transition_risk = {
            (a, b): max(0.0, self.rng.gauss(0.002, 0.0025))
            for a in self.available_primitives for b in self.available_primitives
        }
        for m, program in self.mechanism_programs.items():
            for a, b in zip(program, program[1:]):
                # Correct transitions are low-risk and positively synergistic.
                self.transition_risk[(a, b)] *= 0.25
        self.primitive_side_effect = {
            p: (self.rng.randrange(N_INTERNAL), max(0.0, self.rng.gauss(0.0025, 0.0025)))
            for p in self.available_primitives
        }

        self.internal = [0.925 + self.rng.uniform(-0.018, 0.018) for _ in range(N_INTERNAL)]
        self.prev_core_mean = sum(self.internal[i] for i in core) / core_size
        self.observation_count = 0
        self.repaired = False
        self.permanent_intervention: tuple[str, ...] = ()
        self.alive = True
        self.pending_damage: list[tuple[int, float]] = []
        self.total_cost = 0.0

        passive_core = core[(seed + 3) % core_size]
        passive_visible = tuple(sorted({passive_core, readout}))

        restore_names = [f"r{i}" for i in range(core_size + 5)]
        restore_targets = list(core) + noncore[1:6]
        self.rng.shuffle(restore_targets)
        self.restore_targets = dict(zip(restore_names, restore_targets))
        correct_restore = next(op for op, target in self.restore_targets.items() if target == damaged)

        self.spec = WorldSpec(
            seed=seed,
            relevance=relevance,
            shift_observation=shift_observation,
            self_mechanisms=self.self_mechanisms,
            causal_mechanism=causal,
            nuisance_mechanism=nuisance,
            neutral_mechanism=neutral_mech,
            core_indices=core,
            core_size=core_size,
            topology=self.topology,
            resource_index=resource,
            memory_index=memory,
            sensor_index=sensor,
            mediator_index=mediator,
            damaged_index=damaged,
            readout_index=readout,
            passive_visible_indices=passive_visible,
            intervention_program=self.mechanism_programs[causal],
            program_length=self.program_length,
            restore_operator=correct_restore,
            grammar_family=self.grammar_family,
            role_program=self.role_program,
            label_permuted=self.permute_labels,
            available_primitives=self.available_primitives,
            active_roles=self.active_roles,
            nonstationary=self.nonstationary,
        )

        schedule_rng = random.Random(seed + 8_110_041)
        self.exogenous_schedule = [
            0.0 if t < shift_observation or schedule_rng.random() > 0.30
            else 0.038 + schedule_rng.uniform(-0.005, 0.005)
            for t in range(observation_budget)
        ]

    @property
    def done(self) -> bool:
        return self.observation_count >= self.observation_budget or not self.alive

    def intervention_space_size(self, max_length: int = MAX_PROGRAM_LENGTH) -> int:
        return intervention_space_size(max_length, len(self.available_primitives))

    def memory_capacity(self) -> int:
        value = self.internal[self.spec.memory_index]
        return max(24, min(self.observation_budget, int(24 + (self.observation_budget - 24) * value)))

    def core_neighbors(self, index: int) -> tuple[int, ...]:
        core = self.spec.core_indices
        pos = core.index(index)
        if self.topology == "dense":
            return tuple(i for i in core if i != index)
        if self.topology == "ring":
            return tuple(sorted({core[(pos - 1) % len(core)], core[(pos + 1) % len(core)]}))
        neighbors: list[int] = []
        if pos > 0:
            neighbors.append(core[pos - 1])
        if pos + 1 < len(core):
            neighbors.append(core[pos + 1])
        return tuple(neighbors)

    def intervention_strength(self, mechanism: str, intervention: tuple[str, ...]) -> float:
        if not intervention:
            return 0.0
        if any(p not in self.available_primitives for p in intervention):
            return 0.0
        program = self.mechanism_programs[mechanism]
        seq = tuple(intervention[:MAX_PROGRAM_LENGTH])
        roles = tuple(self.primitive_to_role[p] for p in seq)
        singleton_base = sum(ROLE_SINGLETON_EFFECT[r] for r in roles)
        # Scalar singleton evidence is intentionally ambiguous. For longer programs,
        # directed role interactions carry most of the reusable information.
        base = singleton_base if len(seq) == 1 else 0.18 * singleton_base
        relational = sum(self.role_pair_effect[pair] for pair in zip(roles, roles[1:]))
        positional = sum(self.position_effect[(mechanism, i, p)] for i, p in enumerate(seq)) if len(seq) >= 2 else 0.0
        prefix = 0
        for expected, actual in zip(program, seq):
            if expected != actual:
                break
            prefix += 1
        prefix_bonus = 0.027 * prefix
        correct_transition_bonus = sum(
            0.058 for i, pair in enumerate(zip(seq, seq[1:]))
            if i + 1 < len(program) and pair == (program[i], program[i + 1])
        )
        exact_bonus = 0.350 if seq == program else 0.0
        extra_penalty = 0.060 * max(0, len(seq) - len(program))
        return max(0.0, min(0.98, base + relational + positional + prefix_bonus + correct_transition_bonus + exact_bonus - extra_penalty))

    def intervention_risk(self, intervention: tuple[str, ...]) -> float:
        if any(p not in self.available_primitives for p in intervention):
            return 1.0
        primitive_risk = sum(self.primitive_side_effect[p][1] for p in intervention)
        transition = sum(self.transition_risk[pair] for pair in zip(intervention, intervention[1:]))
        return primitive_risk + transition

    def intervention_is_exact(self, mechanism: str, intervention: tuple[str, ...]) -> bool:
        return tuple(intervention) == self.mechanism_programs[mechanism]

    def intervention_is_functional(self, mechanism: str, intervention: tuple[str, ...]) -> bool:
        return self.intervention_strength(mechanism, intervention) >= 0.78

    def observe(self, action: Action) -> Observation:
        if self.done:
            raise RuntimeError("world finished")
        if action.domain not in DOMAINS:
            raise ValueError(action.domain)
        if action.probe_index >= N_INTERNAL:
            raise ValueError(action.probe_index)
        if any(i < 0 or i >= N_INTERNAL for i in action.sense_indices):
            raise ValueError(action.sense_indices)
        if any(p not in self.available_primitives for p in action.intervention):
            raise ValueError(action.intervention)
        if len(action.intervention) > MAX_PROGRAM_LENGTH:
            raise ValueError("intervention too long")

        index = self.observation_count
        before_full = tuple(self.internal)
        post_shift = index >= self.shift_observation
        domain_mechanisms = self.self_mechanisms if action.domain == "self" else (self.spec.neutral_mechanism,)
        active = tuple(m for m in domain_mechanisms if post_shift and trigger(m, action.bits))

        intervention = tuple(action.intervention)
        strengths = tuple(self.intervention_strength(m, intervention) for m in MECHANISMS)
        effective_active: list[str] = []
        remaining: list[float] = []
        for m in active:
            permanent = self.intervention_strength(m, self.permanent_intervention) if action.domain == "self" else 0.0
            strength = max(self.intervention_strength(m, intervention), permanent)
            remaining.append(max(0.0, 1.0 - strength))
            if self.rng.random() > strength:
                effective_active.append(m)
        external_intensity = max(remaining, default=0.0)
        external_intensity = max(0.0, min(1.2, external_intensity + self.rng.gauss(0.0, 0.010)))

        outcome = base_rule(action.bits)
        if effective_active:
            outcome ^= 1
        sensor_value = self.internal[self.spec.sensor_index]
        noise_probability = 0.012 + 0.18 * max(0.0, 0.90 - sensor_value)
        noise_flip = self.rng.random() < noise_probability
        if noise_flip:
            outcome ^= 1
        residual = int(outcome != base_rule(action.bits))

        pulse_index = action.probe_index if index < self.shift_observation else -1
        if pulse_index >= 0:
            self.internal[pulse_index] -= 0.090
            if pulse_index in self.spec.core_indices:
                for target in self.core_neighbors(pulse_index):
                    self.internal[target] -= 0.034

        sensing_cost = 0.00055 * len(set(action.sense_indices))
        intervention_risk = self.intervention_risk(intervention)
        intervention_cost = 0.00125 * len(intervention) + 0.00030 * max(0, len(intervention) - 1) ** 2
        exposure_cost = 0.0038
        total_action_cost = sensing_cost + intervention_cost + exposure_cost
        self.total_cost += total_action_cost
        self.internal[self.spec.resource_index] -= total_action_cost
        self.internal[self.spec.resource_index] += 0.0038 if residual == 0 else 0.0009

        for primitive in intervention:
            target, magnitude = self.primitive_side_effect[primitive]
            self.internal[target] -= magnitude
        for a, b in zip(intervention, intervention[1:]):
            # Order-sensitive transition side effects change later operation efficacy.
            self.internal[(self.available_primitives.index(b) + self.seed) % N_INTERNAL] -= self.transition_risk[(a, b)]

        due = [item for item in self.pending_damage if item[0] <= index]
        self.pending_damage = [item for item in self.pending_damage if item[0] > index]
        for _, amount in due:
            self.internal[self.spec.damaged_index] -= amount

        if self.relevance == "self_relevant":
            if action.domain == "self" and self.spec.causal_mechanism in effective_active and not action.low_dose:
                self.internal[self.spec.mediator_index] -= 0.035
                self.internal[self.spec.damaged_index] -= 0.018
                self.pending_damage.append((index + 2, 0.018))
            # Conjunctive exposure creates an additional delayed burden.
            if action.domain == "self" and all(m in effective_active for m in self.self_mechanisms) and not action.low_dose:
                self.pending_damage.append((index + 3, 0.008))
        else:
            amount = self.exogenous_schedule[index]
            if amount > 0:
                self.internal[self.spec.damaged_index] -= amount

        self._advance_dynamics(index)
        self.observation_count += 1
        self._check_alive()

        if index < self.shift_observation:
            observed = tuple(range(N_INTERNAL))
        else:
            observed = tuple(sorted(set(self.spec.passive_visible_indices) | set(action.sense_indices)))
        before = tuple(before_full[i] if i in observed else None for i in range(N_INTERNAL))
        after = tuple(self.internal[i] if i in observed else None for i in range(N_INTERNAL))
        return Observation(
            index=index,
            domain=action.domain,
            bits=action.bits,
            outcome=outcome,
            residual=residual,
            external_intensity=external_intensity,
            noise_flip=noise_flip,
            active_mechanisms=active,
            internal_before=before,
            internal_after=after,
            observed_indices=observed,
            pulse_index=pulse_index,
            retained_capacity=self.memory_capacity(),
            intervention=intervention,
            intervention_strengths=strengths,
            intervention_cost=intervention_cost,
            intervention_risk=intervention_risk,
            exposure_cost=exposure_cost,
            sensing_cost=sensing_cost,
        )

    def _advance_dynamics(self, index: int) -> None:
        core = self.spec.core_indices
        old = self.internal[:]
        for i in core:
            neighbors = self.core_neighbors(i)
            neighbor_mean = sum(old[j] for j in neighbors) / max(1, len(neighbors))
            self.internal[i] += 0.046 * (neighbor_mean - old[i]) + 0.023 * (0.94 - old[i]) - 0.00075

        core_mean = sum(self.internal[i] for i in core) / len(core)
        remaining = [i for i in range(N_INTERNAL) if i not in core]
        readout, lagged, oscillator, random_walk, stable = remaining[:5]
        extra = remaining[5:]
        self.internal[readout] = max(0.0, min(1.05, core_mean + self.rng.gauss(0, 0.006)))
        self.internal[lagged] = max(0.0, min(1.05, self.prev_core_mean + self.rng.gauss(0, 0.008)))
        self.internal[oscillator] = 0.72 + 0.15 * math.sin((index + self.seed % 13) / 5.0)
        self.internal[random_walk] += self.rng.gauss(0, 0.014)
        self.internal[stable] += 0.04 * (0.81 - self.internal[stable]) + self.rng.gauss(0, 0.0035)
        for j, i in enumerate(extra):
            target = 0.66 + 0.05 * ((self.seed + j) % 3)
            self.internal[i] += 0.034 * (target - self.internal[i]) + self.rng.gauss(0, 0.005)
        self.prev_core_mean = core_mean
        for i in range(N_INTERNAL):
            self.internal[i] = max(0.0, min(1.08, self.internal[i]))


    def validate_bridge(self, mechanism: str, intervention: tuple[str, ...], trials: int = 12) -> tuple[bool, float, float]:
        """Independent matched-exposure validation before permanent repair."""
        cost = 0.010 + 0.0012 * trials
        self.total_cost += cost
        self.internal[self.spec.resource_index] -= cost
        strength = self.intervention_strength(mechanism, intervention)
        rng = random.Random(self.seed + 771_003 + self.observation_count + sum(ord(c) for c in mechanism))
        untreated, treated = [], []
        for _ in range(trials):
            base = 0.030 + rng.gauss(0.0, 0.003)
            if self.relevance == "self_relevant" and mechanism == self.spec.causal_mechanism:
                untreated.append(base)
                treated.append(base * (1.0 - strength) + rng.gauss(0.0, 0.002))
            else:
                exogenous = 0.026 + rng.gauss(0.0, 0.004)
                untreated.append(exogenous)
                treated.append(exogenous + rng.gauss(0.0, 0.002))
        effect = sum(a - b for a, b in zip(untreated, treated)) / trials
        passed = strength >= 0.64 and effect >= 0.014
        return passed, effect, cost

    def probe_restore(self, operator: str) -> RepairProbe:
        if operator not in self.restore_targets:
            raise ValueError(operator)
        target = self.restore_targets[operator]
        delta = [0.0] * N_INTERNAL
        delta[target] = 0.052
        if target in self.spec.core_indices:
            for neighbor in self.core_neighbors(target):
                delta[neighbor] += 0.014
        return RepairProbe(operator, tuple(delta), 0.003)

    def repair_sequence(self, intervention: tuple[str, ...], restore_operator: str) -> RepairResult:
        before_mean = sum(self.internal[i] for i in self.spec.core_indices) / self.spec.core_size
        strength = self.intervention_strength(self.spec.causal_mechanism, intervention)
        exact = self.intervention_is_exact(self.spec.causal_mechanism, intervention)
        functional = strength >= 0.78
        target = self.restore_targets[restore_operator]
        target_correct = target in set(self.spec.core_indices)
        cost = 0.018 + 0.002 * len(intervention)
        self.total_cost += cost
        self.internal[self.spec.resource_index] -= cost
        if functional:
            self.permanent_intervention = tuple(intervention)
        if target_correct:
            self.internal[target] = max(self.internal[target], 0.86)
            self.internal[self.spec.mediator_index] = max(self.internal[self.spec.mediator_index], 0.84)
            self.internal[self.spec.damaged_index] = max(self.internal[self.spec.damaged_index], 0.84)
            for neighbor in self.core_neighbors(target):
                self.internal[neighbor] = max(self.internal[neighbor], 0.74)
        correct = functional and target_correct
        if correct:
            self.repaired = True
        after_mean = sum(self.internal[i] for i in self.spec.core_indices) / self.spec.core_size
        self._check_alive()
        return RepairResult(tuple(intervention), restore_operator, exact, functional, target_correct, correct, cost, after_mean - before_mean)

    def replication_test(self, intervention: tuple[str, ...], trials: int = 12) -> ReplicationResult:
        if not self.repaired:
            return ReplicationResult(False, False, 0.0, 0.0, 0.0, 0.0)
        cost = 0.014 + 0.0015 * trials
        self.total_cost += cost
        self.internal[self.spec.resource_index] -= cost
        base_strength = self.intervention_strength(self.spec.causal_mechanism, intervention)
        environment_shift = random.Random(self.seed + 91_701).uniform(-0.055, 0.025)
        strength = max(0.0, min(0.98, base_strength + environment_shift))
        blocked = 0
        damage = 0.0
        fresh_rng = random.Random(self.seed + 99_100 + self.observation_count)
        for _ in range(trials):
            if fresh_rng.random() < strength:
                blocked += 1
            else:
                damage += 0.030
        blocked_fraction = blocked / trials
        damage_avoided = max(0.0, 0.030 * trials - damage)
        success = blocked_fraction >= 0.70 and damage <= 0.090
        if not success:
            self.internal[self.spec.damaged_index] -= damage
            self._check_alive()
        return ReplicationResult(True, success, blocked_fraction, damage_avoided, cost, environment_shift)

    def _check_alive(self) -> None:
        values = [self.internal[i] for i in self.spec.core_indices]
        if min(values) <= 0.055 or sum(values) / len(values) <= 0.15:
            self.alive = False
