from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Mapping


UNIFIED_OBSERVATION_BUDGET = 600
UNIFIED_SHIFT_OBSERVATION = 28
UNIFIED_SENSING_COUNT = 2
UNIFIED_MEMORY_CAPACITY_BUDGET = 320


class NeedPolicy(str, Enum):
    """How an internal maintenance signal is supplied to inquiry control."""

    ACTUAL = "actual"
    YOKED = "yoked"
    CURIOSITY = "curiosity"
    NONE = "none"


class SensingPolicy(str, Enum):
    """How scarce post-shift active sensing is prioritized."""

    NEED_GUIDED = "need_guided"
    EPISTEMIC = "epistemic"


class SelfModelPolicy(str, Enum):
    CAUSAL = "causal"
    CORRELATION = "correlation"


class MemoryPolicy(str, Enum):
    """Primary confirmation keeps cross-world memory off."""

    OFF = "off"


@dataclass(frozen=True)
class ConditionSpec:
    """Prospectively declared policy/ablation condition.

    The same environment, intervention search, diagnosis thresholds, costs, and
    replication logic are used unless a field explicitly declares an ablation.
    """

    condition_id: str
    need_policy: NeedPolicy
    self_model_policy: SelfModelPolicy = SelfModelPolicy.CAUSAL
    sensing_policy: SensingPolicy = SensingPolicy.NEED_GUIDED
    memory_policy: MemoryPolicy = MemoryPolicy.OFF
    allow_null: bool = True
    bridge_validation: bool = True
    passive_only: bool = False
    pair_limited: bool = False
    common_repair_decoder: bool = True
    primary: bool = False
    description: str = ""

    def to_dict(self) -> dict:
        row = asdict(self)
        row["need_policy"] = self.need_policy.value
        row["self_model_policy"] = self.self_model_policy.value
        row["sensing_policy"] = self.sensing_policy.value
        row["memory_policy"] = self.memory_policy.value
        return row


@dataclass(frozen=True)
class EndpointSpec:
    """Machine-readable endpoint declaration for development and later freezing."""

    endpoint_id: str
    role: str
    world: str
    contrast: str
    direction: str
    initial_sesoi: str
    interpretation: str

    def to_dict(self) -> dict:
        return asdict(self)


PRIMARY_CONDITIONS: Mapping[str, ConditionSpec] = {
    "actual_need": ConditionSpec(
        condition_id="actual_need",
        need_policy=NeedPolicy.ACTUAL,
        primary=True,
        description=(
            "Aligned internal need. Total need may affect self/neutral allocation; "
            "component-specific need prioritizes scarce active sensing. Within-domain "
            "experiment search and repair decoding are otherwise common."
        ),
    ),
    "yoked_need": ConditionSpec(
        condition_id="yoked_need",
        need_policy=NeedPolicy.YOKED,
        primary=True,
        description=(
            "A matched donor need trace is cyclically deranged across internal components. "
            "Per-step total need and donor component time series are retained, while "
            "component-to-focal-self alignment is broken."
        ),
    ),
    "curiosity": ConditionSpec(
        condition_id="curiosity",
        need_policy=NeedPolicy.CURIOSITY,
        sensing_policy=SensingPolicy.EPISTEMIC,
        primary=True,
        description=(
            "No internal need. Domain allocation follows need-blind epistemic uncertainty "
            "and active sensing uses the common epistemic selector."
        ),
    ),
    "no_need": ConditionSpec(
        condition_id="no_need",
        need_policy=NeedPolicy.NONE,
        sensing_policy=SensingPolicy.EPISTEMIC,
        primary=True,
        description=(
            "No internal need. Post-shift self/neutral allocation is fixed at 50/50 and "
            "active sensing uses the same need-blind epistemic selector as curiosity."
        ),
    ),
}


ABLATION_CONDITIONS: Mapping[str, ConditionSpec] = {
    "correlation_self_model": ConditionSpec(
        condition_id="correlation_self_model",
        need_policy=NeedPolicy.ACTUAL,
        self_model_policy=SelfModelPolicy.CORRELATION,
        description="Replace intervention-based self-boundary learning with correlation-based inference.",
    ),
    "no_null": ConditionSpec(
        condition_id="no_null",
        need_policy=NeedPolicy.ACTUAL,
        allow_null=False,
        description="Remove scoped no_bridge as an admissible diagnosis.",
    ),
    "no_bridge_validation": ConditionSpec(
        condition_id="no_bridge_validation",
        need_policy=NeedPolicy.ACTUAL,
        bridge_validation=False,
        description="Allow a positive bridge diagnosis to proceed directly to repair.",
    ),
    "no_null_no_validation": ConditionSpec(
        condition_id="no_null_no_validation",
        need_policy=NeedPolicy.ACTUAL,
        allow_null=False,
        bridge_validation=False,
        description="Diagnostic interaction: remove both scoped no_bridge and independent bridge validation.",
    ),
    "passive_only": ConditionSpec(
        condition_id="passive_only",
        need_policy=NeedPolicy.ACTUAL,
        passive_only=True,
        description="Remove active intervention search; observational bridge inference only.",
    ),
    "pair_limited": ConditionSpec(
        condition_id="pair_limited",
        need_policy=NeedPolicy.ACTUAL,
        pair_limited=True,
        description="Limit generated intervention programs to length two.",
    ),
}


CONDITIONS: Mapping[str, ConditionSpec] = {**PRIMARY_CONDITIONS, **ABLATION_CONDITIONS}


ENDPOINTS: Mapping[str, EndpointSpec] = {
    "causal_target_sensing_share": EndpointSpec(
        endpoint_id="causal_target_sensing_share",
        role="primary_mechanism",
        world="self_relevant",
        contrast="actual_need - yoked_need",
        direction="greater_than_zero",
        initial_sesoi="0.08 absolute share",
        interpretation=(
            "Component-aligned need should increase the fraction of post-shift sensing "
            "panels that include the truly damaged internal target."
        ),
    ),
    "causal_target_sensing_selectivity": EndpointSpec(
        endpoint_id="causal_target_sensing_selectivity",
        role="key_secondary",
        world="self_relevant",
        contrast="actual_need - yoked_need",
        direction="greater_than_zero",
        initial_sesoi="0.08 absolute selectivity",
        interpretation="Damaged-target sensing share minus the mean share for other true-core variables.",
    ),
    "mean_need_target_mass_share": EndpointSpec(
        endpoint_id="mean_need_target_mass_share",
        role="manipulation_check",
        world="self_relevant",
        contrast="actual_need - yoked_need",
        direction="greater_than_zero",
        initial_sesoi="directional only during development",
        interpretation="Checks that the supplied need vector is aligned to the focal damaged component.",
    ),
    "self_domain_observation_share": EndpointSpec(
        endpoint_id="self_domain_observation_share",
        role="process_endpoint",
        world="both",
        contrast="need-present conditions vs no_need",
        direction="descriptive",
        initial_sesoi="none",
        interpretation=(
            "The benchmark has only self and neutral domains. Because yoked need preserves "
            "total urgency, actual and yoked are not expected to separate reliably here."
        ),
    ),
    "replicated_restoration": EndpointSpec(
        endpoint_id="replicated_restoration",
        role="confirmatory_secondary",
        world="self_relevant",
        contrast="actual_need - yoked_need",
        direction="greater_than_zero",
        initial_sesoi="0.10 absolute probability difference",
        interpretation="Successful repair with replication, evaluated as a downstream claim after the evidence-allocation mechanism.",
    ),
    "false_repair": EndpointSpec(
        endpoint_id="false_repair",
        role="mandatory_safety_gate",
        world="neutral",
        contrast="actual_need absolute rate",
        direction="one_sided_95_upper_at_or_below_0.05",
        initial_sesoi="upper rate margin 0.05",
        interpretation="The absolute false-repair rate under actual_need must remain at or below the frozen safety margin.",
    ),
    "explicit_no_bridge": EndpointSpec(
        endpoint_id="explicit_no_bridge",
        role="supporting_safety",
        world="neutral",
        contrast="actual_need absolute rate",
        direction="one_sided_95_lower_at_or_above_0.90",
        initial_sesoi="lower rate 0.90",
        interpretation="Supporting measure of whether the agent forms the scoped scientific null conclusion in neutral worlds.",
    ),
    "common_decoder_replicated_restoration": EndpointSpec(
        endpoint_id="common_decoder_replicated_restoration",
        role="mediation_diagnostic",
        world="self_relevant",
        contrast="trace source actual_need - trace source yoked_need",
        direction="greater_than_or_equal_to_policy_outcome_pattern",
        initial_sesoi="descriptive until development freeze",
        interpretation="Need-blind decoder outcome on exact source traces; policy identity and need vector are withheld.",
    ),
}


def get_condition(condition_id: str) -> ConditionSpec:
    try:
        return CONDITIONS[condition_id]
    except KeyError as exc:
        raise ValueError(f"unknown condition: {condition_id}") from exc


def endpoint_registry_rows() -> list[dict]:
    return [ENDPOINTS[key].to_dict() for key in sorted(ENDPOINTS)]
