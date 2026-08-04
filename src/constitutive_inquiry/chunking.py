from __future__ import annotations

import csv
from itertools import product
from pathlib import Path
from typing import Iterable, Sequence

from .metrics import aggregate


RUN_KEY = ("split", "seed", "relevance", "mode")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: Sequence[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for field in row:
            if field not in fieldnames:
                fieldnames.append(field)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _merge_keyed(
    row_groups: Iterable[Iterable[dict[str, str]]],
    key_fields: Sequence[str],
    label: str,
    reject_duplicate: bool,
) -> list[dict[str, str]]:
    merged: dict[tuple[str, ...], dict[str, str]] = {}
    for rows in row_groups:
        for row in rows:
            key = tuple(row.get(field, "") for field in key_fields)
            if key in merged:
                if reject_duplicate:
                    raise ValueError(f"duplicate {label} key {key}")
                if merged[key] != row:
                    raise ValueError(f"conflicting {label} row for key {key}")
                continue
            merged[key] = row
    return [merged[key] for key in sorted(merged)]


def _expected_keys(
    split: str,
    seeds: Sequence[int] | None,
    relevances: Sequence[str] | None,
    conditions: Sequence[str] | None,
) -> set[tuple[str, str, str, str]] | None:
    if seeds is None or relevances is None or conditions is None:
        return None
    return {
        (split, str(seed), relevance, condition)
        for seed, relevance, condition in product(sorted(set(seeds)), relevances, conditions)
    }


def merge_unified_chunks(
    chunk_dirs: Sequence[str | Path],
    output_dir: str | Path,
    split: str = "development",
    expected_seeds: Sequence[int] | None = None,
    expected_relevances: Sequence[str] | None = None,
    expected_conditions: Sequence[str] | None = None,
) -> dict[str, int]:
    """Merge chunked unified runs and fail on duplicate, conflict, or missing keys."""

    chunks = [Path(path) for path in chunk_dirs]
    if not chunks:
        raise ValueError("at least one chunk directory is required")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    run_groups = [read_csv_rows(path / f"{split}_run_summaries.csv") for path in chunks]
    if any(not rows for rows in run_groups):
        empty = [str(path) for path, rows in zip(chunks, run_groups) if not rows]
        raise ValueError(f"chunk has no run summary: {empty}")
    runs = _merge_keyed(run_groups, RUN_KEY, "run", reject_duplicate=True)

    actual_keys = {tuple(row[field] for field in RUN_KEY) for row in runs}
    expected = _expected_keys(split, expected_seeds, expected_relevances, expected_conditions)
    if expected is not None:
        missing = sorted(expected - actual_keys)
        unexpected = sorted(actual_keys - expected)
        if missing or unexpected:
            raise ValueError(f"key audit failed: missing={missing[:10]}, unexpected={unexpected[:10]}")

    registry_specs = (
        ("condition_registry", ("condition_id",), False),
        ("endpoint_registry", ("endpoint_id",), False),
        ("yoke_map", ("focal_seed",), False),
    )
    registries: dict[str, list[dict[str, str]]] = {}
    for suffix, key_fields, reject_duplicate in registry_specs:
        groups = [read_csv_rows(path / f"{split}_{suffix}.csv") for path in chunks]
        groups = [rows for rows in groups if rows]
        registries[suffix] = (
            _merge_keyed(groups, key_fields, suffix, reject_duplicate) if groups else []
        )

    write_csv_rows(output / f"{split}_run_summaries.csv", runs)
    write_csv_rows(output / f"{split}_aggregate_metrics.csv", aggregate(runs))
    for suffix, rows in registries.items():
        write_csv_rows(output / f"{split}_{suffix}.csv", rows)

    audit = [{
        "split": split,
        "chunks": len(chunks),
        "run_rows": len(runs),
        "duplicate_run_keys": 0,
        "missing_expected_keys": 0,
        "unexpected_keys": 0,
        "condition_rows": len(registries["condition_registry"]),
        "endpoint_rows": len(registries["endpoint_registry"]),
        "yoke_rows": len(registries["yoke_map"]),
    }]
    write_csv_rows(output / f"{split}_merge_audit.csv", audit)
    return {key: int(value) for key, value in audit[0].items() if key != "split"}
