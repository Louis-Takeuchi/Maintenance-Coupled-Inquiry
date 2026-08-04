# Paper B Phase U1.2 Report
## Component-alignment endpoint correction and common-decoder stabilization

**Date:** 2026-08-04  
**Status:** development complete for implementation phase / confirmatory execution prohibited

## 1. Why this phase was required

The initial unified design treated `self_domain_observation_share` as part of the actual-vs-yoked evidence-allocation test. This was structurally weak because the benchmark has only two external domains (`self`, `neutral`) and the yoked trace preserves total need. Any nonzero need can therefore move both actual and yoked conditions toward the same `self` domain.

A second issue was active-sensing ceiling. Earlier selectors could repeatedly include the damaged target even without aligned need, obscuring the alignment manipulation.

A third issue was common-decoder drift: the source agent and replay decoder contained parallel repair logic and the decoder did not report repair/replication outcomes.

## 2. Changes made

### 2.1 Endpoint correction

- `self_domain_observation_share` is now a process endpoint, not the actual-vs-yoked alignment test.
- Primary evidence-allocation endpoint changed to `causal_target_sensing_share`.
- Added `causal_target_sensing_selectivity`.
- Added manipulation checks:
  - `mean_need_target_mass_share`
  - `mean_need_true_core_mass_share`
  - `mean_sensed_need_mass_share`
  - `need_present_step_share`

### 2.2 Sensing architecture

- Active sensing count fixed at 2 for the current development candidate.
- Actual/yoked use component-specific need-guided sensing.
- Curiosity/no_need use the same need-blind epistemic selector.
- The epistemic selector does not directly reward current predicted-core membership, avoiding the earlier target ceiling.

### 2.3 Yoked manipulation

- Donor is matched on core size, topology, grammar family, primitive cardinality, and nonstationarity.
- Donor component traces are cyclically deranged.
- Per-step total need is preserved.
- Component-to-focal-self alignment is broken.
- The implementation no longer claims independent damage-onset timing.

### 2.4 Common decoder

- Exact replay audit reconstructs actions and hidden side effects.
- Common decoder receives no condition ID, policy ID, or need vector.
- Validation is evaluated on a deep copy of the reconstructed world state.
- Repair selection is shared with the source agent through one need-blind function.
- Common decoder now reports repair, restoration, replication, and replicated-restoration outcomes.

### 2.5 Chunked development execution

- `run_unified_suite` now accepts a relevance subset.
- A frozen yoke-map override can be supplied for single-seed chunks.
- The development CLI refuses focal seeds and donor seeds >=10000.

## 3. Automated validation

- Tests: **38 passed**.
- Short smoke execution: 16 runs, development seeds 0 and 6 only.
- Exact replay in smoke: **16/16**.
- Endpoint registry, condition registry, and yoke map were written to CSV.

## 4. Development-only numerical diagnostic

The following full-budget runs used only seeds 0 and 6. They are implementation diagnostics, not inferential evidence.

### Self-relevant worlds

| Seed | Condition | target need mass | target sensing | diagnosis obs | replicated restoration | common-decoder replicated restoration |
|---:|---|---:|---:|---:|---:|---:|
| 0 | actual | 0.143 | 0.207 | 259 | 1 | 1 |
| 0 | yoked | 0.016 | 0.148 | 269 | 0 | 0 |
| 6 | actual | 0.132 | 0.199 | 276 | 1 | 1 |
| 6 | yoked | 0.012 | 0.099 | 291 | 0 | 0 |

Paired actual-minus-yoked target-sensing differences were approximately +0.060 and +0.099. Actual diagnosis was 10 and 15 observations earlier. In both pairs, the common decoder reproduced the source-trace outcome pattern.

### Neutral worlds

- Source policies made no repair in all four runs.
- Actual and yoked source policies selected `no_bridge` in all four runs.
- One common-decoder replay on a yoked trace proposed an incorrect bridge; this is a decoder diagnostic and shows that source-policy and common-decoder candidate construction are not identical.
- Exact replay was 8/8 across the full-budget development cases.

## 5. Interpretation

The revised manipulation works at the intended component level: actual need places substantially more mass on the focal damaged variable than yoked need, while total urgency and self-domain allocation can remain similar.

The two-seed outcome pattern is encouraging but must not be treated as confirmation. It could disappear, reverse, or depend on a small subset of world strata across seeds 0–39.

The common-decoder result supports the feasibility of evidence-trace mediation analysis, but it also revealed an important limitation: a common decoder reconstructed from observation history can choose a different candidate than the source controller. This is expected for a diagnostic decoder and must be reported rather than hidden.

## 6. What is not complete

- No calibration seed was used.
- No confirmatory seed was used.
- No paired interval analysis across development seeds 0–39 is complete.
- No source freeze or pre-run manifest exists.
- No final SESOI is frozen.
- No partial-bridge world is implemented.
- No claim about external problem-domain formation is supported.

## 7. Next required phase

Phase U1.3 should implement:

1. deterministic chunk merge with duplicate/missing-key audit;
2. paired development analysis across seeds 0–39;
3. difficulty controls at the candidate budget;
4. freeze-or-STOP decision without examining confirmatory seeds.
