# Frozen Confirmation Analysis Plan v0.14

## Cohorts

- Training: seeds 0–31, 32 self-relevant worlds, budget 360.
- Development: seeds 15000–15007 and 16000–16003; all excluded from confirmation.
- Confirmation: seeds 18000–18039, 40 worlds.
- Planned reproduction pool: unused seeds beginning at 18100. The implemented deterministic audit used seed 18100, four representative modes, and two independent executions; see the provenance audit.

Each confirmation seed is evaluated under self-relevant and neutral relevance for all ten conditions, giving 800 confirmation runs.

## Frozen parameters

- observation budget: 280;
- shift observation: 28;
- core size: 5 or 6;
- primitive cardinality: 5 for even seeds and 7 for odd seeds;
- primitive-label permutation: enabled;
- nonstationarity: seeds congruent to 3 modulo 4;
- alignment-posterior top-k: 6;
- memory execution gate: mapping trust ≥ 0.06, normalized entropy ≤ 0.20, held-out support ≥ 0.70;
- protected local beam width: 4;
- expansions per mechanism: 7;
- paired bootstrap draws: 20,000.

No execution parameter or threshold is changed after confirmation begins.

## Conditions

1. `confidence_gated_relational_generation` — posterior alignment, execution gate, protected local beam, quarantine and rollback.
2. `ungated_relational_generation` — top-alignment memory without confidence gating.
3. `reset_actual_generation` — full current-world relational calibration, no cross-world memory.
4. `sparse_reset_generation` — sparse calibration used by the gated modes, no memory.
5. `posterior_no_quarantine_generation` — posterior machinery without quarantine or rollback.
6. `quarantine_no_local_reservation_generation` — quarantine but no guaranteed local-search beam.
7. `frozen_correct_memory_generation` — trained memory loaded but not revised.
8. `adversarial_wrong_memory_generation` — permuted memory behind the same confidence gate.
9. `oracle_family_generation` — true intervention program supplied.
10. `no_null_confidence_gated_generation` — forced-positive control.

## Primary targets

1. Principal restoration difference versus full reset is at least −0.05.
2. Principal restoration difference versus sparse reset is at least −0.05.
3. Principal neutral false-repair rate is below 0.05.
4. Principal sequence reduction versus full reset is at least 15%.
5. Principal sequence reduction versus sparse reset is at least 5%.
6. Memory changes the selected action in at least 20% of self-relevant worlds.
7. At least 80% of adversarial-memory action changes are detected before repair.
8. Nonstationary restoration is no more than 10 percentage points below stationary restoration.

Targets 2 and 5 are decisive for a cross-world-memory benefit. Targets 3 and 4 alone are insufficient because sparse current-world calibration can produce safety and lower cost without memory.

## Statistical procedures

- Wilson 95% intervals for proportions where reported.
- Paired seed bootstrap with 20,000 draws for condition differences and sequence-reduction ratios.
- Confirmation is analyzed only after all 800 rows are present, seed-complete, and duplicate-free.
- Null, negative, and non-evaluable outcomes are reported without replacement by post-hoc targets.
