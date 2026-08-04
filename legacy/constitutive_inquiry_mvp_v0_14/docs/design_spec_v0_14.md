# Design Specification v0.14 — Confidence-Gated Relational Transfer

## Research problem

v0.13 showed that a single best cross-world graph alignment could narrow inquiry incorrectly. In seven-operation worlds containing a novel decoy, relational memory restored only 87.5% of self-relevant worlds versus 100% for reset search.

v0.14 asks whether transferred intervention memory can be used only when current-world evidence warrants trust, while preserving a complete local fallback.

## Agent architecture

The agent retains the v0.13 causal microworld, self-boundary learner, explicit `no_bridge` hypothesis, reversible interventions, independent bridge validation, repair, and replication test.

The transfer layer adds:

1. **Alignment posterior** — top-k primitive-to-role graph mappings are retained rather than only the minimum-cost mapping.
2. **Disjoint support** — ordered role pairs are deterministically split into mapping-fit and held-out validation sets.
3. **Entropy-aware trust** — trust combines leading posterior mass, held-out support, memory energy, and posterior concentration.
4. **Execution gate** — remembered programs are executable only when mapping trust is at least 0.06, normalized alignment entropy is at most 0.20, and held-out support is at least 0.70.
5. **Protected local beam** — transferred sequences and local sequences have separate parents; memory cannot become the sole parent of later search.
6. **Quarantine and rollback** — failed transferred candidates are quarantined by grammar family; failed-world updates are rolled back to a checkpoint before decay.
7. **Nonstationarity** — one quarter of evaluation worlds perturb the role-interaction law, testing whether old ontology is rejected.

## Operation worlds

- Five-operation worlds omit one irrelevant canonical role.
- Seven-operation worlds add a novel decoy.
- Primitive labels are independently permuted.
- Core size is five or six.
- Held-out grammar families are `branch_comp` and `context_comp`.
- Evaluation alternates stationary and nonstationary worlds.

## Conditions

1. `confidence_gated_relational_generation` — full posterior, entropy gate, local beam reservation, quarantine, rollback.
2. `ungated_relational_generation` — v0.13-style top alignment and unrestricted relational prior.
3. `reset_actual_generation` — full relational calibration, no cross-world memory.
4. `sparse_reset_generation` — same sparse calibration as gated modes, no memory; isolates calibration savings.
5. `posterior_no_quarantine_generation` — posterior gate and local reservation, but no quarantine/rollback after failure.
6. `quarantine_no_local_reservation_generation` — posterior proposals and quarantine, but memory may narrow local search despite uncertainty.
7. `frozen_correct_memory_generation` — trained memory is never revised.
8. `adversarial_wrong_memory_generation` — strongly permuted templates with the same confidence gate and rollback.
9. `oracle_family_generation` — true intervention program supplied.
10. `no_null_confidence_gated_generation` — forced positive explanation control.

## Interpretation rule

The method counts as successful only if it both:

- preserves recovery relative to reset search; and
- reduces search relative to `sparse_reset_generation` while actually executing memory proposals.

A safe result produced by rejecting every memory proposal is explicitly classified as a failed transfer result, not a successful memory system.

## Scope

The relation ontology, memory substrate, energy decay, damage law, repair operators, and stopping conditions remain stipulated in software. v0.14 evaluates epistemic trust in transfer; it does not implement constitutive death or constitutive normativity.
