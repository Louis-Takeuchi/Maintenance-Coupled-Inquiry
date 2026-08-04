# Provenance Audit v0.14

## Cohort history

- Training used seeds 0–31 and produced `results/training/relational_memory.json`.
- Algorithm development used seeds 15000–15007 and 16000–16003.
- A preliminary confirmation using seeds 17000–17039 was rejected after auditing timestamps and discovering that `agent.py` had changed after those results were generated.
- The current execution code was then frozen, the training memory was regenerated with that code, and final confirmation used only seeds 18000–18039.
- Reproduction used unused seed 18100.

The rejected 17000-series results are not included in the formal confirmation tables.

## Training memory

The final frozen training table contains 32 self-relevant worlds and 25 recoveries. No failed training world was removed. The resulting memory hash is recorded in `docs/frozen_memory_hash_v0_14.txt`.

## Confirmation completeness

The final confirmation table contains:

- 800 rows;
- 40 unique seeds;
- 10 conditions;
- two relevance classes;
- exactly one row per `(mode, seed, relevance)` key;
- no duplicate keys;
- seed range 18000–18039 for every mode.

The execution environment terminated several long or parallel aggregate commands. Completed rows were retained, and each condition was resumed in a single process. The runner skips already-completed `(seed, relevance)` pairs, so resumed execution did not duplicate or replace outcomes.

## Runtime freeze

The simulation-execution manifest includes:

- `pyproject.toml`;
- experiment and condition runners;
- the environment, agent, cross-world memory, experiment, metrics, model, and self-model modules.

`docs/frozen_execution_runtime_manifest_v0_14.txt` records these files before final confirmation. `docs/evaluated_execution_runtime_manifest_v0_14.txt` records them after all 800 runs. The manifests are identical.

The broader runtime manifest additionally includes analysis and reproduction utilities. Those utilities changed after simulation for the following documented reasons:

- `analyze_v0_14.py` was updated to require the final 18000–18039 cohort, to avoid pandas attribute access on the `mode` column, and to use the Wilson proportion interval specified in the frozen plan;
- `run_reproduction_audit_v0_14.py` was reduced to a representative audit that can complete within the execution environment.

Neither utility is part of the simulation-execution manifest, and neither change modifies stored run summaries.

## Analysis

Analysis was run only after all 800 formal rows were present. It generated:

- `results/confirmation_run_summaries.csv`;
- `results/confirmation_aggregate_metrics.csv`;
- `results/primary_target_results.csv`;
- `results/key_evaluation_contrasts.csv`;
- `results/failure_cases.csv`;
- `results/transfer_by_cardinality_and_stationarity.csv`;
- `results/memory_counterfactual_summary.csv`.

Paired contrasts use 20,000 seed-level bootstrap draws. Proportion intervals use Wilson 95% score intervals as specified in the frozen analysis plan.

## Reproduction deviation and result

The frozen plan proposed all ten modes on unused seeds 18100–18101, run twice. The full audit repeatedly exceeded the execution environment's process/time limits. The final audit was therefore reduced to four representative conditions on unused seed 18100:

- principal confidence-gated memory;
- matched sparse reset;
- no-local-reservation memory;
- forced-positive null ablation.

Each run contains both relevance classes, giving 8 rows per independent run. The two normalized row sets, raw CSV bytes, and SHA-256 hashes were identical. This is a narrower determinism audit than originally planned and should not be described as a full ten-condition reproduction.

## Final audit status

- execution code unchanged across confirmation: yes;
- frozen training memory unchanged across confirmation: yes;
- formal confirmation rows: 800;
- duplicate formal keys: 0;
- automated tests: 20 passed;
- representative reproduction audit: passed;
- formal result based on seeds 18000–18039 only: yes.
