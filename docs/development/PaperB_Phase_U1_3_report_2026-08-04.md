# Paper B Phase U1.3 Report
## Chunk-safe execution, merge audit, and paired development analysis

**Date:** 2026-08-04  
**Status:** implementation complete / development-only / confirmation remains prohibited

## 1. Purpose

Full-budget unified runs exceed a single execution window when many conditions and worlds are evaluated together. A confirmatory workflow therefore requires deterministic chunk execution without allowing donor-yoke mappings, condition registries, or result keys to drift across chunks.

This phase implemented the execution and analysis infrastructure needed to split runs safely.

## 2. Implemented changes

### 2.1 Chunk-safe development runner

`run_unified_development.py` now supports:

- focal seed subsets;
- relevance subsets (`self_relevant`, `neutral`);
- condition subsets;
- an explicit frozen yoke-map CSV;
- common-decoder execution per chunk.

The development wrapper rejects:

- focal seeds >=10000;
- yoke donor seeds >=10000.

The default observation budget and shift are imported from the protocol registry, preventing CLI drift.

### 2.2 Frozen yoke-map override

`run_unified_suite` accepts a yoke-map override and verifies:

- every focal seed has a donor;
- donor differs from focal;
- focal and donor match on the frozen world stratum.

This permits one focal world to be executed per process while preserving the prospectively declared donor mapping.

### 2.3 Deterministic chunk merger

`combine_unified_chunks.py` and `constitutive_inquiry.chunking`:

- merge run summaries by `(split, seed, relevance, mode)`;
- reject duplicate run keys;
- reject conflicting condition, endpoint, or yoke rows;
- optionally require an exact expected key grid;
- report missing and unexpected keys;
- regenerate aggregate metrics from merged rows;
- emit a merge-audit CSV.

### 2.4 Paired development analysis

`analyze_unified_development.py` and `constitutive_inquiry.development_analysis`:

- pair actual and yoked rows within seed and relevance;
- calculate per-seed differences;
- summarize mean, median, range, and sign consistency;
- keep development diagnostics separate from later confirmatory inference.

## 3. Automated validation

- **38 tests passed**.
- Tests include:
  - yoke stratum matching;
  - component derangement and total-need preservation;
  - need-blind repair invariance;
  - endpoint-role declaration;
  - exact replay fields;
  - frozen-map single-seed chunk execution;
  - duplicate-key rejection;
  - expected-key audit;
  - paired contrast direction.

## 4. Eight-chunk development audit

Eight full-budget chunks were executed for:

- seeds: 0, 6;
- relevance: self-relevant, neutral;
- conditions: actual_need, yoked_need.

Merge result:

| Field | Result |
|---|---:|
| chunks | 8 |
| run rows | 8 |
| duplicate run keys | 0 |
| missing expected keys | 0 |
| unexpected keys | 0 |
| condition rows | 2 |
| endpoint rows | 7 |
| yoke rows | 2 |

Exact replay succeeded in all 8 full-budget runs.

## 5. Paired development diagnostic

These numbers use two development seeds only and are not inferential results.

### Self-relevant actual minus yoked

| Metric | Mean difference | Sign consistency |
|---|---:|---:|
| target need mass share | +0.1237 | 2/2 positive |
| target sensing share | +0.0795 | 2/2 positive |
| target sensing selectivity | +0.0163 | 1/2 positive |
| diagnosis observations | −12.5 | 2/2 earlier for actual |
| replicated restoration | +1.0 | 2/2 positive |
| common-decoder replicated restoration | +1.0 | 2/2 positive |

The target-sensing mean is approximately the initial +0.08 SESOI but cannot be treated as meeting it with only two development seeds.

### Neutral actual minus yoked

- false repair difference: 0.0;
- source-policy false repair: 0 in all four neutral runs;
- common decoder made one incorrect bridge decision on a yoked trace, which remains a documented diagnostic limitation.

## 6. Current STOP decision

The implementation is now capable of chunked development execution and audited recombination. It is **not ready for confirmation** because the following remain incomplete:

1. development execution across seeds 0–39;
2. difficulty-control evaluation at the 380-observation candidate budget;
3. paired interval estimation and final SESOI freeze;
4. source and analysis hash freeze;
5. final donor map for confirmatory seeds;
6. pre-run manifest and confirmation-only wrapper.

## 7. Next phase

Phase U1.4 should run the full development grid and difficulty controls in audited chunks, then issue one of two decisions:

- **FREEZE:** the first parameter set satisfies the prospectively stated calibration criteria;
- **STOP/REDESIGN:** floor, ceiling, or manipulation failure remains.

No confirmatory seed should be opened during U1.4.
