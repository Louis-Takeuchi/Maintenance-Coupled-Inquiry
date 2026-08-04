# Constitutive Inquiry MVP v0.14

A reproducible simulation benchmark for **confidence-gated cross-world intervention memory** in self-relevant scientific inquiry.

## Research question

v0.13 showed negative transfer when an uncertain relational alignment was allowed to narrow inquiry. v0.14 asks whether transferred intervention memory becomes beneficial when the agent keeps several candidate alignments, validates them in the current world, reserves a protected local-search beam, and quarantines failed transfers.

A matched `sparse_reset_generation` control uses the same reduced current-world calibration but no cross-world memory. This control isolates the contribution of memory content from the contribution of sparse calibration.

## Main result: the gate made memory safe by making it inert

| Condition | Self-relevant restoration | Mean sequences | Memory changed action | Neutral false repair |
|---|---:|---:|---:|---:|
| Confidence-gated memory | **100.0%** | **45.125** | **0.0%** | 0.0% |
| Full reset | 97.5% | 57.275 | 0.0% | 0.0% |
| Sparse reset, no memory | **100.0%** | **45.125** | 0.0% | 0.0% |
| Ungated relational memory | 95.0% | 59.325 | 45.0% | 0.0% |
| Posterior, no quarantine | 100.0% | 45.125 | 0.0% | 0.0% |
| No protected local beam | 52.5% | 44.675 | 85.0% | 0.0% |
| Frozen trained memory | 100.0% | 45.125 | 0.0% | 0.0% |
| Adversarial memory behind gate | 100.0% | 45.125 | 0.0% | 0.0% |
| Oracle | 100.0% | 1.000 | 0.0% | 0.0% |
| Positive explanation forced | 100.0% | 45.125 | 0.0% | **100.0%** |

The principal condition evaluated 21.2% fewer sequences than full reset (paired-bootstrap 95% interval 17.7%–24.3%). However, it was exactly identical to sparse reset in both restoration and sequence count.

The transferred-memory proposal was tested in **0 of 40 self-relevant worlds**. Its Wilson 95% interval was 0%–8.8%. Mean mapping trust was approximately `2.64e-5`, while normalized alignment entropy was approximately `0.990`. The gate therefore rejected every transferred proposal.

The correct conclusion is:

> Confidence gating prevented negative transfer by falling back entirely to memory-free sparse local search. It did not establish a beneficial use of cross-world memory.

## Decisive controls

### Matched sparse reset

- Confidence-gated memory: 100% restoration, 45.125 sequences.
- Sparse reset without memory: 100% restoration, 45.125 sequences.
- Difference in restoration: 0.00.
- Relative sequence reduction: 0.00%.

This shows that the apparent improvement over full reset came from sparse current-world calibration, not from transferred memory.

### Ungated memory

Ungated relational memory changed action in 45% of self-relevant worlds, but restored 95% and evaluated 59.325 sequences. Memory was active, yet it was neither safer nor more efficient than the matched memory-free control.

### Removing protected local search

Without a guaranteed local beam, memory changed action in 85% of self-relevant worlds and restoration fell to 52.5%. The local reserve is therefore strongly protective, but protection alone does not make memory useful.

### Forced positive explanation

The main condition made no false repairs in 40 neutral worlds. The Wilson 95% interval is 0%–8.8%. When `no_bridge` was prohibited, all 40 neutral worlds were falsely repaired. Explicit causal rejection remains essential.

## Training memory

The frozen memory was trained on 32 self-relevant worlds and recovered 25 of them (78.1%). Performance by training family was:

| Family | Recovery |
|---|---:|
| `repeat` | 8/8 |
| `delayed` | 8/8 |
| `inhibitor_first` | 6/8 |
| `fork` | 3/8 |

The stored memory therefore contained genuine but uneven experience. Its non-use in confirmation cannot be explained by an empty training phase.

## Frozen evaluation

- Training seeds: 0–31, 32 self-relevant worlds, budget 320.
- Development seeds: 15000–15007 and 16000–16003; excluded from confirmation.
- Discarded exploratory confirmation: 17000–17039, rejected after detecting a runtime-version mismatch.
- Final confirmation seeds: 18000–18039.
- Conditions: 10.
- Relevance classes: self-relevant and neutral.
- Confirmation runs: 800, with no duplicate `(mode, seed, relevance)` keys.
- Observation budget: 280.
- Paired-bootstrap draws: 20,000.
- Execution-source manifest before and after confirmation: identical.
- Automated tests: 20 passed.
- Reproduction audit: four representative conditions on unused seed 18100, run independently twice; 8 rows per run and byte-identical CSVs.

The frozen plan proposed a larger ten-condition, two-seed reproduction audit. It was reduced because the execution environment repeatedly terminated the full audit. This deviation is recorded in `docs/provenance_audit_v0_14.md`.

## Interpretation

v0.14 distinguishes three outcomes that must not be conflated:

1. **unsafe transfer** — memory changes action and harms inquiry;
2. **beneficial transfer** — memory changes action and improves inquiry relative to a matched no-memory control;
3. **vacuous safety** — memory is always rejected and the system succeeds through local search alone.

The final principal condition is outcome 3.

The relation ontology, memory substrate, energy decay, damage law, repair operators, and stopping conditions remain stipulated in software. The benchmark evaluates epistemic control of transfer; it does not implement constitutive death or constitutive normativity.

## Reproduce

```bash
cd constitutive_inquiry_mvp_v0_14
python -m pip install -e .
pytest -q
python analyze_v0_14.py
python run_reproduction_audit_v0_14.py
```

See:

- `docs/design_spec_v0_14.md`
- `docs/confirmation_analysis_plan_v0_14.md`
- `docs/evaluation_note_v0_14.md`
- `docs/provenance_audit_v0_14.md`
- `docs/freeze_audit_v0_14.txt`
- `docs/next_steps_v0_15.md`
