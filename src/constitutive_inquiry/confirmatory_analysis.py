from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
import random
from typing import Iterable, Mapping, Sequence


CONFIRMATORY_BOOTSTRAP_SEED = 941_731
CONFIRMATORY_BOOTSTRAP_REPLICATES = 50_000
CONFIRMATORY_ALPHA = 0.05


STRATUM_FIELDS = (
    "core_size",
    "grammar_family",
    "primitive_cardinality",
    "nonstationary",
    "topology",
)


@dataclass(frozen=True)
class Interval:
    lower: float
    upper: float


def world_stratum(row: Mapping[str, object]) -> tuple[str, ...]:
    """Return the frozen generator stratum carried by a run-summary row."""

    return tuple(str(row[field]) for field in STRATUM_FIELDS)


def percentile(values: Sequence[float], probability: float) -> float:
    """Linear-interpolated percentile without a third-party dependency."""

    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = probability * (len(ordered) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    weight = position - lower_index
    return ordered[lower_index] * (1.0 - weight) + ordered[upper_index] * weight


def stratified_paired_bootstrap_mean_interval(
    rows: Iterable[Mapping[str, object]],
    *,
    difference_field: str = "difference",
    stratum_field: str = "stratum",
    seed: int = CONFIRMATORY_BOOTSTRAP_SEED,
    replicates: int = CONFIRMATORY_BOOTSTRAP_REPLICATES,
    alpha: float = CONFIRMATORY_ALPHA,
) -> Interval:
    """Percentile interval for a paired mean, resampling pairs within frozen strata.

    Each input row represents one paired world contrast. Resampling within stratum
    preserves the prospectively fixed generator composition while treating worlds
    within a stratum as the sampling units.
    """

    if replicates < 1:
        raise ValueError("replicates must be positive")
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row[stratum_field])].append(float(row[difference_field]))
    if not grouped:
        raise ValueError("bootstrap requires at least one row")

    rng = random.Random(seed)
    bootstrap_means: list[float] = []
    total_n = sum(len(values) for values in grouped.values())
    for _ in range(replicates):
        total = 0.0
        for values in grouped.values():
            for _ in range(len(values)):
                total += values[rng.randrange(len(values))]
        bootstrap_means.append(total / total_n)
    return Interval(
        lower=percentile(bootstrap_means, alpha / 2.0),
        upper=percentile(bootstrap_means, 1.0 - alpha / 2.0),
    )


def _binomial_cdf(x: int, n: int, p: float) -> float:
    return sum(math.comb(n, k) * (p**k) * ((1.0 - p) ** (n - k)) for k in range(x + 1))


def clopper_pearson_upper(x: int, n: int, alpha: float = CONFIRMATORY_ALPHA) -> float:
    """One-sided exact upper confidence bound for a binomial proportion."""

    if n <= 0 or not 0 <= x <= n:
        raise ValueError("require n > 0 and 0 <= x <= n")
    if x == n:
        return 1.0
    if x == 0:
        return 1.0 - alpha ** (1.0 / n)
    low, high = 0.0, 1.0
    for _ in range(100):
        mid = (low + high) / 2.0
        if _binomial_cdf(x, n, mid) > alpha:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def clopper_pearson_lower(x: int, n: int, alpha: float = CONFIRMATORY_ALPHA) -> float:
    """One-sided exact lower confidence bound for a binomial proportion."""

    if n <= 0 or not 0 <= x <= n:
        raise ValueError("require n > 0 and 0 <= x <= n")
    return 1.0 - clopper_pearson_upper(n - x, n, alpha)


def mean_difference(rows: Iterable[Mapping[str, object]], field: str = "difference") -> float:
    values = [float(row[field]) for row in rows]
    if not values:
        raise ValueError("mean requires at least one row")
    return sum(values) / len(values)


def mechanism_verdict(
    *,
    manipulation_mean: float,
    manipulation_interval: Interval,
    sensing_mean: float,
    sensing_interval: Interval,
    sensing_sesoi: float,
    neutral_false_repairs: int,
    neutral_n: int,
    false_repair_margin: float,
    exact_replay_rate: float,
) -> str:
    """Frozen three-way verdict for the main evidence-allocation claim."""

    safety_upper = clopper_pearson_upper(neutral_false_repairs, neutral_n)
    safety_lower = clopper_pearson_lower(neutral_false_repairs, neutral_n)
    if manipulation_mean <= 0.0 or manipulation_interval.upper <= 0.0:
        return "not_supported"
    if sensing_mean <= 0.0 or sensing_interval.upper <= 0.0:
        return "not_supported"
    if safety_lower > false_repair_margin or exact_replay_rate < 1.0:
        return "not_supported"
    if (
        manipulation_interval.lower > 0.0
        and sensing_mean >= sensing_sesoi
        and sensing_interval.lower > 0.0
        and safety_upper <= false_repair_margin
    ):
        return "supported"
    return "indeterminate"


def downstream_verdict(
    *,
    restoration_mean: float,
    restoration_interval: Interval,
    restoration_sesoi: float,
    safety_status: str,
) -> str:
    """Frozen verdict for the downstream replicated-restoration claim."""

    if safety_status == "not_supported" or restoration_mean <= 0.0 or restoration_interval.upper <= 0.0:
        return "not_supported"
    if safety_status == "supported" and restoration_mean >= restoration_sesoi and restoration_interval.lower > 0.0:
        return "supported"
    return "indeterminate"
