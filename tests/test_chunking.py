import csv

import pytest

from constitutive_inquiry.chunking import merge_unified_chunks
from constitutive_inquiry.unified_experiment import run_unified_suite


def test_chunk_merge_audits_expected_keys(tmp_path):
    chunk0 = tmp_path / "chunk0"
    chunk6 = tmp_path / "chunk6"
    run_unified_suite(
        chunk0,
        seeds=[0],
        split="development",
        condition_ids=["actual_need"],
        relevance_levels=["self_relevant"],
        budget=2,
        shift=0,
    )
    run_unified_suite(
        chunk6,
        seeds=[6],
        split="development",
        condition_ids=["actual_need"],
        relevance_levels=["self_relevant"],
        budget=2,
        shift=0,
    )
    output = tmp_path / "combined"
    audit = merge_unified_chunks(
        [chunk0, chunk6],
        output,
        expected_seeds=[0, 6],
        expected_relevances=["self_relevant"],
        expected_conditions=["actual_need"],
    )
    assert audit["run_rows"] == 2
    with (output / "development_run_summaries.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert {(row["seed"], row["mode"]) for row in rows} == {("0", "actual_need"), ("6", "actual_need")}


def test_chunk_merge_rejects_duplicate_run_keys(tmp_path):
    chunk = tmp_path / "chunk"
    run_unified_suite(
        chunk,
        seeds=[0],
        split="development",
        condition_ids=["actual_need"],
        relevance_levels=["self_relevant"],
        budget=2,
        shift=0,
    )
    with pytest.raises(ValueError, match="duplicate run key"):
        merge_unified_chunks([chunk, chunk], tmp_path / "combined")


def test_paired_development_summary_preserves_direction():
    from constitutive_inquiry.development_analysis import paired_contrasts

    rows = [
        {"seed": "0", "relevance": "self_relevant", "mode": "actual_need", "causal_target_sensing_share": "0.8", "core_size": "5", "grammar_family": "g", "primitive_cardinality": "5", "nonstationary": "False", "topology": "ring"},
        {"seed": "0", "relevance": "self_relevant", "mode": "yoked_need", "causal_target_sensing_share": "0.2", "core_size": "5", "grammar_family": "g", "primitive_cardinality": "5", "nonstationary": "False", "topology": "ring"},
    ]
    pairs, summary = paired_contrasts(rows, metrics=("causal_target_sensing_share",))
    assert pairs[0]["difference"] == pytest.approx(0.6)
    assert pairs[0]["stratum"] == "5|g|5|False|ring"
    assert summary[0]["positive_fraction"] == 1.0
