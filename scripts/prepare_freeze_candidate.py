from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_DIR = ROOT / "manifests"
FREEZE_MANIFEST = MANIFEST_DIR / "freeze_candidate_file_manifest_v0_3.csv"
FREEZE_HASH = MANIFEST_DIR / "freeze_candidate_file_manifest_v0_3.sha256"
PRE_RUN = MANIFEST_DIR / "PRE_RUN_MANIFEST_CANDIDATE_v0_3.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def selected_files() -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    root_files = [
        "pyproject.toml",
        "README.md",
        "analyze_confirmatory_candidate.py",
        "analyze_unified_development.py",
        "combine_unified_chunks.py",
        "run_common_decoder_case.py",
        "run_unified_development.py",
        "run_unified_confirmation.py",
        "prepare_freeze_candidate.py",
        "audit_freeze_candidate.py",
    ]
    for name in root_files:
        path = ROOT / name
        if path.exists():
            scope = "runtime" if name.startswith("run_") or name.startswith("combine_") else "analysis"
            rows.append((scope, path))

    for path in sorted((ROOT / "src" / "constitutive_inquiry").glob("*.py")):
        rows.append(("source", path))
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        rows.append(("test", path))

    docs = [
        "UNIFIED_CONFIRMATORY_PROTOCOL_CANDIDATE_v0_3.md",
        "PHASE_U1_4_DEVELOPMENT_GRID_AND_FREEZE_CANDIDATE_REPORT.md",
        "PHASE_U1_4A_SIX_SEED_REPLAY_AND_NEUTRAL_SAFETY_REPORT.md",
        "DEVELOPMENT_CALIBRATION_REPORT_v0_3.md",
        "DEVELOPMENT_ABLATION_REPORT_v0_3.md",
        "DEVELOPMENT_PARAMETER_REGISTRY_v0_3.csv",
        "ENDPOINT_REGISTRY_DRAFT_v0_3.csv",
        "DEVELOPMENT_RESULTS_PRIMARY_v0_3.csv",
        "DEVELOPMENT_RESULTS_ABLATIONS_v0_3.csv",
        "DEVELOPMENT_PAIRED_ACTUAL_YOKED_v0_3.csv",
        "COMMON_DECODER_REPLAY_AUDIT_v0_3.csv",
        "COMMON_DECODER_REPLAY_SUMMARY_v0_3.csv",
        "SOURCE_CHANGELOG_v0_3.md",
    ]
    for name in docs:
        path = ROOT / "docs" / name
        if path.exists():
            rows.append(("protocol_or_report", path))

    base_manifests = [
        "condition_registry_v0_3.csv",
        "endpoint_implementation_registry_v0_3.csv",
        "sesoi_verdict_registry_v0_3.csv",
        "world_generator_registry_v0_3.json",
        "seed_manifest_v0_3.csv",
        "confirmatory_yoke_map_v0_3.csv",
        "primary_chunk_plan_v0_3.csv",
        "ablation_chunk_plan_v0_3.csv",
        "expected_key_grid_v0_3.json",
        "development_yoke_map_0_39_v0_2.csv",
    ]
    for name in base_manifests:
        path = MANIFEST_DIR / name
        if path.exists():
            rows.append(("registry", path))

    development_evidence = [
        ROOT / "results" / "development" / "u1_4_primary_0_39_merged" / "development_run_summaries.csv",
        ROOT / "results" / "development" / "u1_4_primary_0_39_merged" / "development_merge_audit.csv",
        ROOT / "results" / "development" / "u1_4_candidate_interval_diagnostic_50k" / "candidate_endpoint_intervals.csv",
        ROOT / "results" / "development" / "u1_4_candidate_interval_diagnostic_50k" / "candidate_verdict_diagnostic.csv",
        ROOT / "results" / "development" / "candidate_v0_3_budget600_6seeds" / "development_run_summaries.csv",
        ROOT / "results" / "development" / "ablations_v0_3_budget600_6seeds" / "development_run_summaries.csv",
    ]
    for path in development_evidence:
        if path.exists():
            rows.append(("development_evidence", path))

    return rows


def main() -> None:
    entries = []
    for scope, path in selected_files():
        entries.append(
            {
                "relative_path": path.relative_to(ROOT).as_posix(),
                "scope": scope,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    entries.sort(key=lambda row: row["relative_path"])
    with FREEZE_MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "scope", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(entries)

    freeze_hash = sha256_file(FREEZE_MANIFEST)
    FREEZE_HASH.write_text(f"{freeze_hash}  {FREEZE_MANIFEST.name}\n", encoding="utf-8")

    registry_names = [
        "condition_registry_v0_3.csv",
        "endpoint_implementation_registry_v0_3.csv",
        "sesoi_verdict_registry_v0_3.csv",
        "world_generator_registry_v0_3.json",
        "seed_manifest_v0_3.csv",
        "confirmatory_yoke_map_v0_3.csv",
        "primary_chunk_plan_v0_3.csv",
        "ablation_chunk_plan_v0_3.csv",
        "expected_key_grid_v0_3.json",
    ]
    pre_run = {
        "protocol_version": "v0.3",
        "status": "LOCKED_NOT_ACTIVATED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "confirmatory_outcome_episodes_executed": 0,
        "activation_manifest_present": (MANIFEST_DIR / "CONFIRMATION_ACTIVATION.json").exists(),
        "freeze_candidate_manifest": FREEZE_MANIFEST.relative_to(ROOT).as_posix(),
        "freeze_candidate_manifest_sha256": freeze_hash,
        "parameters": {
            "observation_budget": 600,
            "shift_observation": 28,
            "active_sensing_width": 2,
            "primary_memory": "off",
        },
        "confirmatory_design": {
            "focal_seed_start": 30000,
            "focal_seed_end": 30071,
            "focal_n": 72,
            "primary_source_rows": 576,
            "primary_replay_rows": 288,
            "ablation_source_rows": 432,
            "primary_chunks": 48,
            "ablation_chunks": 72,
            "bootstrap_seed": 941731,
            "bootstrap_replicates": 50000,
        },
        "registry_sha256": {
            name: sha256_file(MANIFEST_DIR / name) for name in registry_names
        },
        "required_before_execution": [
            "freeze readiness audit PASS",
            "no confirmatory outcome files present",
            "explicit user approval after Phase U1.5 review",
            "activation manifest anchored to this pre-run manifest and freeze hash",
        ],
        "note": "This manifest prepares but does not authorize confirmatory execution.",
    }
    PRE_RUN.write_text(json.dumps(pre_run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {FREEZE_MANIFEST.relative_to(ROOT)}")
    print(f"freeze manifest SHA-256: {freeze_hash}")
    print(f"wrote locked pre-run manifest: {PRE_RUN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
