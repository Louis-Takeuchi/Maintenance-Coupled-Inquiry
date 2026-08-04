import pytest

from constitutive_inquiry.confirmatory_analysis import (
    Interval,
    clopper_pearson_lower,
    clopper_pearson_upper,
    downstream_verdict,
    mechanism_verdict,
    stratified_paired_bootstrap_mean_interval,
)


def test_exact_binomial_bounds_cover_zero_event_safety_design():
    assert clopper_pearson_upper(0, 72) < 0.05
    assert clopper_pearson_upper(0, 40) > 0.05
    assert clopper_pearson_lower(72, 72) > 0.90


def test_stratified_bootstrap_is_deterministic_and_directional():
    rows = [
        {"stratum": "a", "difference": 0.1},
        {"stratum": "a", "difference": 0.2},
        {"stratum": "b", "difference": 0.3},
        {"stratum": "b", "difference": 0.4},
    ]
    first = stratified_paired_bootstrap_mean_interval(rows, seed=7, replicates=1000)
    second = stratified_paired_bootstrap_mean_interval(rows, seed=7, replicates=1000)
    assert first == second
    assert first.lower > 0.0


def test_mechanism_verdict_distinguishes_supported_and_indeterminate():
    supported = mechanism_verdict(
        manipulation_mean=0.10,
        manipulation_interval=Interval(0.04, 0.16),
        sensing_mean=0.12,
        sensing_interval=Interval(0.03, 0.20),
        sensing_sesoi=0.08,
        neutral_false_repairs=0,
        neutral_n=72,
        false_repair_margin=0.05,
        exact_replay_rate=1.0,
    )
    assert supported == "supported"
    indeterminate = mechanism_verdict(
        manipulation_mean=0.10,
        manipulation_interval=Interval(0.04, 0.16),
        sensing_mean=0.06,
        sensing_interval=Interval(-0.01, 0.13),
        sensing_sesoi=0.08,
        neutral_false_repairs=0,
        neutral_n=72,
        false_repair_margin=0.05,
        exact_replay_rate=1.0,
    )
    assert indeterminate == "indeterminate"


def test_downstream_verdict_requires_safety_and_positive_interval():
    assert downstream_verdict(
        restoration_mean=0.20,
        restoration_interval=Interval(0.05, 0.35),
        restoration_sesoi=0.10,
        safety_status="supported",
    ) == "supported"
    assert downstream_verdict(
        restoration_mean=0.20,
        restoration_interval=Interval(0.05, 0.35),
        restoration_sesoi=0.10,
        safety_status="not_supported",
    ) == "not_supported"
    assert downstream_verdict(
        restoration_mean=0.20,
        restoration_interval=Interval(0.05, 0.35),
        restoration_sesoi=0.10,
        safety_status="indeterminate",
    ) == "indeterminate"
