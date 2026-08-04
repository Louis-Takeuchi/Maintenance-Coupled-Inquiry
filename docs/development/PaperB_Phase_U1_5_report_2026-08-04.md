# Paper B Phase U1.5 Report
## Freeze-readiness audit and locked confirmatory package

**Date:** 2026-08-04  
**Status:** **PASS — LOCKED_NOT_ACTIVATED**  
**Confirmatory outcome episodes executed:** **0**

## 1. Conclusion

The v0.3 confirmatory package passed the pre-run machine audit. The protocol, implementation registries, seed manifest, stratum-matched yoke map, expected-key grids, chunk plans, analysis settings, development evidence, replay evidence, and technical execution lock are mutually consistent.

This result authorizes only the statement that the package is **ready for explicit human review**. It does not authorize confirmatory execution. No activation manifest exists, and the confirmatory wrapper exits before constructing an outcome episode.

## 2. Audit result

- checks: **16**
- passed: **16**
- failed: **0**
- automated tests: **45 passed**
- freeze status: `PASS_LOCKED_NOT_ACTIVATED`

Audited categories:

1. condition registry vs implementation;
2. endpoint registry vs implementation;
3. world parameters vs implementation constants;
4. deterministic confirmatory yoke map;
5. nine-stratum seed composition;
6. development/confirmatory/bootstrap seed roles;
7. primary expected-key coverage;
8. ablation expected-key coverage;
9. expected-key count registry;
10. 320-run development merge integrity;
11. 50,000-replicate analysis smoke test;
12. 48/48 exact development replay;
13. absence of confirmatory outcome records;
14. absence of activation manifest;
15. freeze-manifest hash consistency;
16. automated test suite.

## 3. Frozen candidate execution design

### Primary confirmation

- focal seeds: **30000–30071**
- focal N: **72**
- worlds: `self_relevant`, `neutral`
- primary conditions: `actual_need`, `yoked_need`, `curiosity`, `no_need`
- source rows: **576**
- exact replay/common-decoder rows: **288**
- chunks: **48**

### Confirmatory ablations

- conditions: six prespecified ablations
- designated world per ablation
- source rows: **432**
- chunks: **72**

### Analysis

- sampling unit: paired focal seed
- resampling: generator-stratum-preserving paired bootstrap
- bootstrap seed: **941731**
- bootstrap replicates: **50,000**
- safety interval: one-sided 95% exact Clopper–Pearson

## 4. Seed and stratum audit

The 72 focal seeds form nine generator strata:

- three even-seed strata with 12 focal worlds each;
- six odd-seed strata with 6 focal worlds each.

The confirmatory yoke map contains 72 deterministic rows. Every donor:

- differs from its focal seed;
- belongs to the same frozen generator stratum;
- uses the frozen non-zero cyclic component shift;
- is marked `outcome_episode_executed = 0`.

Generating this map used seed-derived configuration metadata only. No confirmatory outcome episode was run.

## 5. Safety sample-size rationale

The 40-seed development grid produced 0/40 neutral false repairs for `actual_need`, but its one-sided 95% exact upper bound is approximately 0.072, above the 0.05 safety margin. This makes the development candidate verdict indeterminate even though the observed count is zero.

N=72 provides adequate zero-event resolution: 0/72 gives a one-sided 95% exact upper bound below 0.05. This is a prospective sample-size rationale, not a favorable-result claim.

## 6. Exact-replay provenance correction

During U1.5, an audit detected that the convenience directory `candidate_v0_3_budget600_6seeds` had been overwritten by a non-replay export. The original 48-row exact-replay dataset remained intact under the earlier development directory.

A new read-only canonical copy was created:

`results/development/candidate_v0_3_budget600_6seeds_exact_replay_immutable`

It contains:

- 6 development seeds;
- 4 primary conditions;
- 2 relevance classes;
- 48/48 exact replay matches;
- no confirmatory seeds;
- source-file SHA-256 records.

The overwritten convenience directory is excluded from freeze evidence. The incident is retained in provenance rather than silently erased.

## 7. Technical execution lock

`run_unified_confirmation.py` does not accept arbitrary seed lists. It accepts only a frozen chunk ID from the primary or ablation plan.

Execution additionally requires a separate `CONFIRMATION_ACTIVATION.json` that must:

- record explicit user approval;
- use the exact v0.3 approval token;
- match the protocol version;
- match the freeze-candidate manifest hash;
- match the current pre-run manifest hash.

That activation file does not exist. A lock dry-run exits before any experimental world is executed.

## 8. Current STOP boundary

Phase U1.5 is complete, but confirmation remains stopped.

The next action is not an automatic experiment run. It is a human review of:

- protocol v0.3;
- endpoint and SESOI hierarchy;
- N=72 design;
- seed and donor manifests;
- 48 primary chunks;
- 72 ablation chunks;
- exact-replay requirement;
- activation boundary.

Only after explicit approval should an activation manifest be created. Primary confirmation should then be run before the confirmatory ablations, without opening or adapting to intermediate outcomes.
