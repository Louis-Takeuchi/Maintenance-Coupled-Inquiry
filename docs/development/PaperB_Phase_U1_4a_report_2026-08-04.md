# Paper B Phase U1.4a Report
## Six-seed exact-replay closure and neutral safety audit

**Date:** 2026-08-04  
**Status:** development-only audit complete / confirmatory execution remains prohibited

## 1. Scope

This phase resumed from the U1.3 STOP point and completed the six-development-seed exact-replay audit for the primary `actual_need` and `yoked_need` contrast.

Frozen development settings:

- seeds: `0,2,4,6,8,10`;
- relevance classes: `self_relevant`, `neutral`;
- observation budget: `600`;
- shift observation: `28`;
- active sensing width: `2`;
- yoke map: the frozen six-seed development map;
- source-policy decoder and common decoder use the shared need-blind repair-selection function;
- no seed `>=10000` was opened.

This is not the full U1.4 development grid. It closes the six-seed replay and neutral-safety prerequisite before a 0–39 development run.

## 2. Execution audit

Twenty-four full-budget runs were executed as seed × relevance × condition chunks.

| Audit field | Result |
|---|---:|
| run rows | 24 |
| duplicate run keys | 0 |
| missing expected keys | 0 |
| unexpected keys | 0 |
| exact replays | 24/24 |
| condition registry rows | 2 |
| endpoint registry rows | 7 |
| frozen yoke rows | 6 |
| automated tests | 38 passed |

## 3. Neutral-world safety

All twelve neutral runs reached the correct scoped null decision.

| Condition | Explicit `no_bridge` | Source false repair | Common-decoder bridge correct | Common-decoder false repair |
|---|---:|---:|---:|---:|
| actual_need | 6/6 | 0/6 | 6/6 | 0/6 |
| yoked_need | 6/6 | 0/6 | 6/6 | 0/6 |

The common decoder did not attempt repair in any neutral run.

The single common-decoder neutral error documented in the earlier U1.3 diagnostic was not reproduced after the shared repair/decoder implementation. It is retained as an old-implementation observation, not silently deleted.

Component-target sensing differs strongly between actual and yoked even in neutral worlds because an exogenous internal damage target still exists. This is a manipulation/process measure, not evidence of an external causal bridge. The safety verdict is determined by bridge validation, repair behavior, and false repair.

## 4. Self-relevant development diagnostic

### 4.1 Condition means

| Metric | actual_need | yoked_need | Actual − yoked |
|---|---:|---:|---:|
| Mean need mass on damaged target | 0.1940 | 0.0242 | +0.1698 |
| Damaged-target sensing share | 0.2826 | 0.0886 | +0.1941 |
| Target sensing selectivity | 0.1389 | −0.0221 | +0.1610 |
| Mean diagnosis observation | 266.0 | 271.7 | −5.7 |
| Replicated restoration | 6/6 | 3/6 | +3/6 |
| Common-decoder replicated restoration | 6/6 | 3/6 | +3/6 |

### 4.2 Sign consistency

- damaged-target need mass: actual > yoked in 6/6 pairs;
- damaged-target sensing share: actual > yoked in 5/6 pairs;
- diagnosis occurred earlier under actual in 5/6 pairs;
- replicated restoration favored actual in 3/6 pairs and tied in 3/6;
- common-decoder replicated restoration showed exactly the same 3 positive / 3 tied pattern.

### 4.3 Interpretation

The yoke manipulation preserves a nonzero need process while substantially disrupting component-to-focal-target alignment. Under the same need-blind decoder, source traces from actual and yoked conditions retain the same outcome pattern as their source policies.

This supports the intended mediation interpretation at the development level: the observed contrast is carried by evidence acquisition and diagnosis traces rather than by a condition-specific repair formula.

It does **not** establish a confirmatory effect. Six inspected development seeds cannot determine the final SESOI, sampling interval, or paper-level verdict.

## 5. Current decision

### PASS for this subphase

- six-seed neutral safety audit;
- 24/24 exact replay;
- source/common-decoder consistency;
- chunk merge integrity;
- manipulation alignment at the damaged component;
- automated regression suite.

### STOP before confirmation

The following remain incomplete:

1. the full development grid over seeds 0–39 at the frozen candidate settings;
2. all four primary conditions in that full grid;
3. full difficulty-control and ablation validation on the selected development set;
4. paired interval estimation and final SESOI/verdict freeze;
5. source, analysis, endpoint, and donor-map hash freeze;
6. pre-run manifest and a separate confirmation-only wrapper.

No confirmatory seed may be opened.

## 6. Next executable step

Run U1.4b as audited chunks over development seeds 0–39. Start with the four primary conditions and both relevance classes, merge against an exact expected key grid, then evaluate the prospectively stated floor/ceiling and manipulation criteria. If the candidate fails, issue STOP/REDESIGN rather than tuning on confirmatory data.
