from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from constitutive_inquiry.confirmation_lock import ConfirmationLocked, validate_activation
from constitutive_inquiry.protocol import (
    CONDITIONS,
    ENDPOINTS,
    UNIFIED_MEMORY_CAPACITY_BUDGET,
    UNIFIED_OBSERVATION_BUDGET,
    UNIFIED_SENSING_COUNT,
    UNIFIED_SHIFT_OBSERVATION,
)
from constitutive_inquiry.unified_experiment import (
    build_yoke_map,
    evaluation_world_config,
    yoke_component_shift,
)


ROOT = Path(__file__).resolve().parent
M = ROOT / "manifests"
OUT = ROOT / "results" / "development" / "u1_5_freeze_readiness_audit"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main() -> None:
    checks: list[dict[str, str]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "status": "PASS" if condition else "FAIL", "detail": detail})

    condition_rows = read_csv(M / "condition_registry_v0_3.csv")
    expected_conditions = {key: {k: str(v) for k, v in spec.to_dict().items()} for key, spec in CONDITIONS.items()}
    actual_conditions = {row["condition_id"]: row for row in condition_rows}
    condition_ok = set(actual_conditions) == set(expected_conditions)
    if condition_ok:
        for key, expected in expected_conditions.items():
            for field, value in expected.items():
                if actual_conditions[key].get(field) != value:
                    condition_ok = False
                    break
    check("REG-CONDITION", condition_ok, f"rows={len(condition_rows)}, code_conditions={len(expected_conditions)}")

    endpoint_rows = read_csv(M / "endpoint_implementation_registry_v0_3.csv")
    expected_endpoints = {key: {k: str(v) for k, v in spec.to_dict().items()} for key, spec in ENDPOINTS.items()}
    actual_endpoints = {row["endpoint_id"]: row for row in endpoint_rows}
    endpoint_ok = set(actual_endpoints) == set(expected_endpoints)
    if endpoint_ok:
        for key, expected in expected_endpoints.items():
            for field, value in expected.items():
                if actual_endpoints[key].get(field) != value:
                    endpoint_ok = False
                    break
    check("REG-ENDPOINT", endpoint_ok, f"rows={len(endpoint_rows)}, code_endpoints={len(expected_endpoints)}")

    endpoint_hierarchy_ok = (
        ENDPOINTS["causal_target_sensing_share"].role == "primary_mechanism"
        and ENDPOINTS["causal_target_sensing_share"].initial_sesoi == "0.08 absolute share"
        and ENDPOINTS["false_repair"].role == "mandatory_safety_gate"
        and ENDPOINTS["false_repair"].contrast == "actual_need absolute rate"
        and ENDPOINTS["replicated_restoration"].role == "confirmatory_secondary"
        and ENDPOINTS["replicated_restoration"].initial_sesoi == "0.10 absolute probability difference"
        and ENDPOINTS["explicit_no_bridge"].role == "supporting_safety"
    )
    check("REG-ENDPOINT-HIERARCHY", endpoint_hierarchy_ok, "primary mechanism / mandatory safety / confirmatory secondary are separated")

    sesoi_rows = read_csv(M / "sesoi_verdict_registry_v0_3.csv")
    sesoi_by_endpoint = {row["endpoint"]: row for row in sesoi_rows}
    sesoi_ok = (
        sesoi_by_endpoint["causal_target_sensing_share"]["role"] == "primary_mechanism"
        and sesoi_by_endpoint["false_repair"]["role"] == "mandatory_safety_gate"
        and sesoi_by_endpoint["false_repair"]["contrast"] == "actual_need absolute rate"
        and sesoi_by_endpoint["replicated_restoration"]["role"] == "confirmatory_secondary"
        and sesoi_by_endpoint["explicit_no_bridge"]["role"] == "supporting_safety"
    )
    check("REG-SESOI-HIERARCHY", sesoi_ok, f"rows={len(sesoi_rows)}")

    world = json.loads((M / "world_generator_registry_v0_3.json").read_text(encoding="utf-8"))
    world_ok = (
        world["observation_budget"] == UNIFIED_OBSERVATION_BUDGET == 600
        and world["shift_observation"] == UNIFIED_SHIFT_OBSERVATION == 28
        and world["active_sensing_width"] == UNIFIED_SENSING_COUNT == 2
        and world["memory_capacity_reference"] == UNIFIED_MEMORY_CAPACITY_BUDGET == 320
        and world["primary_memory"] == "off"
        and world["confirmatory_seed_range"] == [30000, 30071]
    )
    check("REG-WORLD", world_ok, "budget/shift/sensing/memory/seed range agree with code")

    focal_seeds = list(range(30000, 30072))
    yoke_rows = read_csv(M / "confirmatory_yoke_map_v0_3.csv")
    yoke = {int(row["focal_seed"]): int(row["donor_seed"]) for row in yoke_rows}
    yoke_expected = build_yoke_map(focal_seeds)
    yoke_ok = yoke == yoke_expected and len(yoke_rows) == 72
    for row in yoke_rows:
        focal = int(row["focal_seed"])
        donor = int(row["donor_seed"])
        expected_stratum = "|".join(map(str, evaluation_world_config(focal).stratum()))
        yoke_ok &= donor != focal
        yoke_ok &= evaluation_world_config(focal).stratum() == evaluation_world_config(donor).stratum()
        yoke_ok &= row["stratum"] == expected_stratum
        yoke_ok &= int(row["component_shift"]) == yoke_component_shift(focal, donor)
        yoke_ok &= row["outcome_episode_executed"] == "0"
    check("REG-YOKE", yoke_ok, f"rows={len(yoke_rows)}, deterministic stratum-matched map, no outcome episodes")

    stratum_counts = Counter("|".join(map(str, evaluation_world_config(seed).stratum())) for seed in focal_seeds)
    check("DESIGN-STRATA", len(stratum_counts) == 9 and sorted(stratum_counts.values()) == [6, 6, 6, 6, 6, 6, 12, 12, 12], str(dict(stratum_counts)))

    seed_rows = read_csv(M / "seed_manifest_v0_3.csv")
    seed_index = {int(row["seed"]): row for row in seed_rows}
    seed_ok = all(seed_index[s]["role"] == "development" and seed_index[s]["status"] == "executed" for s in range(40))
    seed_ok &= all(seed_index[s]["role"] == "confirmatory_focal" and seed_index[s]["status"] == "sealed_not_executed" for s in focal_seeds)
    seed_ok &= seed_index[941731]["role"] == "bootstrap_analysis"
    check("REG-SEED", seed_ok, f"development=40, sealed confirmatory=72, analysis RNG=1")

    primary_rows = read_csv(M / "primary_chunk_plan_v0_3.csv")
    primary_keys: list[tuple[int, str, str]] = []
    replay_keys: list[tuple[int, str, str]] = []
    primary_plan_ok = len(primary_rows) == 48
    for row in primary_rows:
        seeds = [int(v) for v in parse_list(row["seeds"])]
        relevances = parse_list(row["relevance"])
        conditions = parse_list(row["conditions"])
        expanded = [(seed, rel, cond) for seed in seeds for rel in relevances for cond in conditions]
        primary_keys.extend(expanded)
        primary_plan_ok &= len(expanded) == int(row["expected_source_rows"])
        if int(row["common_decoder"]):
            replay_keys.extend(expanded)
            primary_plan_ok &= set(conditions) == {"actual_need", "yoked_need"}
    expected_primary = {(seed, rel, cond) for seed in focal_seeds for rel in ("self_relevant", "neutral") for cond in ("actual_need", "yoked_need", "curiosity", "no_need")}
    primary_plan_ok &= len(primary_keys) == len(set(primary_keys)) == 576
    primary_plan_ok &= set(primary_keys) == expected_primary
    primary_plan_ok &= len(replay_keys) == len(set(replay_keys)) == 288
    check("PLAN-PRIMARY", primary_plan_ok, f"chunks={len(primary_rows)}, source_keys={len(primary_keys)}, replay_keys={len(replay_keys)}")

    ablation_rows = read_csv(M / "ablation_chunk_plan_v0_3.csv")
    ablation_keys: list[tuple[int, str, str]] = []
    ablation_plan_ok = len(ablation_rows) == 72
    for row in ablation_rows:
        seeds = [int(v) for v in parse_list(row["seeds"])]
        relevances = parse_list(row["relevance"])
        conditions = parse_list(row["conditions"])
        expanded = [(seed, rel, cond) for seed in seeds for rel in relevances for cond in conditions]
        ablation_keys.extend(expanded)
        ablation_plan_ok &= len(expanded) == int(row["expected_source_rows"])
        ablation_plan_ok &= int(row["common_decoder"]) == 0
    ablation_plan_ok &= len(ablation_keys) == len(set(ablation_keys)) == 432
    check("PLAN-ABLATION", ablation_plan_ok, f"chunks={len(ablation_rows)}, source_keys={len(ablation_keys)}")

    expected_grid = json.loads((M / "expected_key_grid_v0_3.json").read_text(encoding="utf-8"))
    grid_ok = expected_grid == {
        "primary_source_rows": 576,
        "primary_replay_rows": 288,
        "primary_chunks": 48,
        "ablation_source_rows": 432,
        "ablation_chunks": 72,
        "confirmatory_focal_n": 72,
    }
    check("PLAN-EXPECTED-GRID", grid_ok, json.dumps(expected_grid, sort_keys=True))

    merge_rows = read_csv(ROOT / "results" / "development" / "u1_4_primary_0_39_merged" / "development_merge_audit.csv")
    merge = merge_rows[0]
    merge_ok = merge["run_rows"] == "320" and all(merge[k] == "0" for k in ("duplicate_run_keys", "missing_expected_keys", "unexpected_keys"))
    check("DEV-MERGE", merge_ok, str(merge))

    diagnostic_rows = read_csv(ROOT / "results" / "development" / "u1_4_candidate_interval_diagnostic_50k" / "candidate_endpoint_intervals.csv")
    diagnostic_ok = len(diagnostic_rows) == 4 and all(row["bootstrap_replicates"] == "50000" and row["bootstrap_seed"] == "941731" for row in diagnostic_rows)
    check("DEV-ANALYSIS-50K", diagnostic_ok, f"endpoint_rows={len(diagnostic_rows)}")

    replay_rows = read_csv(ROOT / "docs" / "COMMON_DECODER_REPLAY_AUDIT_v0_3.csv")
    exact_count = sum(float(row.get("replay_exact_match", "0")) == 1.0 for row in replay_rows)
    replay_conditions = {row.get("trace_source_condition") for row in replay_rows}
    replay_budgets = {row.get("budget") for row in replay_rows}
    replay_keys = {
        (row.get("seed"), row.get("relevance"), row.get("trace_source_condition"))
        for row in replay_rows
    }
    expected_replay_keys = {
        (str(seed), relevance, condition)
        for seed in (0, 2, 4, 6, 8, 10)
        for relevance in ("self_relevant", "neutral")
        for condition in ("actual_need", "yoked_need")
    }
    replay_ok = (
        len(replay_rows) == 24
        and exact_count == 24
        and replay_conditions == {"actual_need", "yoked_need"}
        and replay_budgets == {"600"}
        and replay_keys == expected_replay_keys
    )
    check("DEV-EXACT-REPLAY", replay_ok, f"exact={exact_count}/{len(replay_rows)}, budget={sorted(replay_budgets)}")

    confirm_seed_hits: list[str] = []
    results_root = ROOT / "results"
    for path in results_root.rglob("*.csv"):
        if "confirmation" in path.parts:
            confirm_seed_hits.append(f"confirmation-path:{path.relative_to(ROOT)}")
            continue
        name = path.name.lower()
        if "run_summaries" not in name and "step_traces" not in name:
            continue
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            raw = row.get("seed", "")
            if raw and raw.lstrip("-").isdigit() and 30000 <= int(raw) <= 30071:
                confirm_seed_hits.append(f"seed-hit:{path.relative_to(ROOT)}:{raw}")
                break
    check("BLIND-NO-CONFIRM-OUTCOMES", not confirm_seed_hits, "none" if not confirm_seed_hits else "; ".join(confirm_seed_hits[:10]))

    pre = M / "PRE_RUN_MANIFEST_CANDIDATE_v0_3.json"
    activation = M / "CONFIRMATION_ACTIVATION.json"
    lock_ok = False
    try:
        validate_activation(pre, activation)
    except ConfirmationLocked:
        lock_ok = True
    check("LOCK-ACTIVATION", lock_ok and not activation.exists(), "activation manifest absent; wrapper remains locked")

    pre_data = json.loads(pre.read_text(encoding="utf-8"))
    freeze_manifest = ROOT / pre_data["freeze_candidate_manifest"]
    freeze_hash = hashlib.sha256(freeze_manifest.read_bytes()).hexdigest()
    pre_ok = (
        pre_data["status"] == "LOCKED_NOT_ACTIVATED"
        and pre_data["confirmatory_outcome_episodes_executed"] == 0
        and pre_data["activation_manifest_present"] is False
        and pre_data["freeze_candidate_manifest_sha256"] == freeze_hash
    )
    check("FREEZE-HASH", pre_ok, f"freeze_manifest_sha256={freeze_hash}")

    freeze_rows = read_csv(freeze_manifest)
    file_hash_failures: list[str] = []
    for row in freeze_rows:
        path = ROOT / row["relative_path"]
        if not path.is_file():
            file_hash_failures.append(f"missing:{row['relative_path']}")
            continue
        actual_size = path.stat().st_size
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_size != int(row["size_bytes"]):
            file_hash_failures.append(f"size:{row['relative_path']}")
        if actual_hash != row["sha256"]:
            file_hash_failures.append(f"sha256:{row['relative_path']}")
    check(
        "FREEZE-FILE-HASHES",
        not file_hash_failures,
        f"verified={len(freeze_rows)}" if not file_hash_failures else "; ".join(file_hash_failures[:10]),
    )

    registry_hashes = pre_data.get("registry_sha256", {})
    registry_hash_ok = bool(registry_hashes)
    for name, expected_hash in registry_hashes.items():
        path = M / name
        registry_hash_ok &= path.is_file()
        if path.is_file():
            registry_hash_ok &= hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash
    check("PRE-RUN-REGISTRY-HASHES", registry_hash_ok, f"registries={len(registry_hashes)}")

    test_run = subprocess.run(["pytest", "-q"], cwd=ROOT, text=True, capture_output=True)
    test_ok = test_run.returncode == 0 and "45 passed" in test_run.stdout
    check("TESTS", test_ok, test_run.stdout.strip().splitlines()[-1] if test_run.stdout.strip() else test_run.stderr.strip())

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "freeze_readiness_audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "detail"])
        writer.writeheader()
        writer.writerows(checks)

    failures = [row for row in checks if row["status"] != "PASS"]
    summary = {
        "phase": "U1.5",
        "status": "PASS_LOCKED_NOT_ACTIVATED" if not failures else "FAIL_STOP",
        "checks": len(checks),
        "passed": len(checks) - len(failures),
        "failed": len(failures),
        "failure_ids": [row["check_id"] for row in failures],
        "confirmatory_outcome_episodes_executed": 0,
    }
    (OUT / "freeze_readiness_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "pytest_output.txt").write_text(test_run.stdout + test_run.stderr, encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
