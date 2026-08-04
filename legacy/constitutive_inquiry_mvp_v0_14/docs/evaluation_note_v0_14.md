# Evaluation Note v0.14

## Conclusion

The intended v0.14 claim was not supported.

The confidence-gated condition restored all 40 self-relevant worlds and made no false repairs in 40 neutral worlds. It also evaluated 21.2% fewer sequences than full reset. However, it never executed a transferred-memory proposal and was exactly identical to the matched sparse-reset control.

Thus the correct interpretation is not “safe beneficial transfer,” but:

> The trust gate avoided negative transfer by rejecting memory completely and reverting to memory-free sparse local search.

## Confirmation cohort

- seeds 18000–18039;
- 40 worlds;
- two relevance classes;
- ten conditions;
- 800 total runs;
- budget 280;
- five-operation worlds on even seeds;
- seven-operation worlds on odd seeds;
- nonstationary relation law when `seed % 4 == 3`.

## Main results

| Condition | Restoration | Mean evaluated sequences | Memory changed action | Neutral false repair |
|---|---:|---:|---:|---:|
| Principal confidence-gated memory | 1.000 | 45.125 | 0.000 | 0.000 |
| Full reset | 0.975 | 57.275 | 0.000 | 0.000 |
| Sparse reset | 1.000 | 45.125 | 0.000 | 0.000 |
| Ungated memory | 0.950 | 59.325 | 0.450 | 0.000 |
| Posterior without quarantine | 1.000 | 45.125 | 0.000 | 0.000 |
| No local-beam reservation | 0.525 | 44.675 | 0.850 | 0.000 |
| Frozen memory | 1.000 | 45.125 | 0.000 | 0.000 |
| Adversarial memory behind gate | 1.000 | 45.125 | 0.000 | 0.000 |
| Oracle | 1.000 | 1.000 | 0.000 | 0.000 |
| Forced positive | 1.000 | 45.125 | 0.000 | 1.000 |

Wilson 95% intervals for selected proportions:

- principal restoration 100%: 91.2%–100%;
- full-reset restoration 97.5%: 87.1%–99.6%;
- principal neutral false repair 0%: 0%–8.8%;
- principal memory-proposal execution 0%: 0%–8.8%;
- forced-positive neutral false repair 100%: 91.2%–100%.

## Paired contrasts

- Principal − full-reset restoration: +0.025, 95% interval 0.000 to +0.075.
- Principal − sparse-reset restoration: 0.000, interval 0.000 to 0.000.
- Principal − ungated restoration: +0.050, interval 0.000 to +0.125.
- Principal − no-local-reservation restoration: +0.475, interval +0.325 to +0.625.
- Principal − full-reset sequences: −12.150, interval −14.875 to −9.449.
- Principal − sparse-reset sequences: 0.000, interval 0.000 to 0.000.
- Relative sequence reduction versus full reset: 21.2%, interval 17.7% to 24.3%.
- Relative sequence reduction versus sparse reset: 0.0%, interval 0.0% to 0.0%.
- Principal − forced-positive neutral false repair: −1.000.

## Frozen target status

Met by point estimate:

- restoration noninferiority versus full reset;
- restoration noninferiority versus sparse reset;
- principal neutral false repair below 5%;
- at least 15% sequence reduction versus full reset;
- five-versus-seven operation stability;
- nonstationary performance-drop limit.

Failed:

- at least 5% sequence reduction versus sparse reset;
- memory proposal execution in at least 20% of self-relevant worlds;
- the combined “memory not merely ignored” requirement.

Not evaluable:

- adversarial-memory detection before repair, because adversarial memory never changed an action.

The 0% neutral false-repair point estimate meets the frozen threshold, but its Wilson upper bound is 8.8%; the sample does not establish a sub-5% population rate with 95% confidence.

## Why the gate rejected everything

In the principal condition:

- mean mapping trust was approximately `2.64e-5`;
- normalized alignment entropy was approximately `0.990`;
- memory proposals tested: 0/40 self-relevant worlds;
- memory changed action: 0/40 self-relevant worlds;
- the same values held in neutral worlds.

The posterior remained too diffuse to cross the action gate. Frozen trained memory and adversarial memory produced the same behavioral result because both were ignored.

## What the ablations show

### Protected local beam

Removing local-beam reservation reduced restoration to 52.5%. Memory changed action in 85% of self-relevant worlds. The protected local branch is therefore a safety mechanism.

However, the protected principal condition was identical to sparse reset. Local fallback was sufficient for performance and left no demonstrated contribution for memory.

### Ungated transfer

Ungated memory changed action in 45% of self-relevant worlds, restored 95%, and evaluated 59.325 sequences. This proves that the trained memory can alter inquiry, but not that it helps: it underperformed sparse reset and used more search than full reset.

### Posterior and quarantine ablations

`posterior_no_quarantine_generation`, `frozen_correct_memory_generation`, and `adversarial_wrong_memory_generation` all matched sparse reset exactly because their memory proposals never crossed the gate. Their high recovery is safe non-use, not successful correction.

### Explicit null

Forcing a positive explanation caused false repair in every neutral world. The explicit `no_bridge` option remains essential even when transferred memory is inactive.

## Cardinality and nonstationarity

The principal condition restored 100% in:

- five-operation stationary worlds;
- seven-operation stationary worlds;
- seven-operation nonstationary worlds.

This stability cannot be attributed to change detection or robust transfer, because memory never changed action. It shows only that sparse local search handled these confirmation worlds.

## Training-memory limitation

Training restored 25/32 worlds. `repeat` and `delayed` were learned reliably, while `fork` was recovered in only 3/8 worlds. The confirmation gate was therefore applied to a real but uneven memory object.

## Scientific interpretation

The final v0.14 result separates safety from usefulness:

> A transfer controller is not successful merely because harmful memories are rejected. To demonstrate beneficial memory, the stored experience must change inquiry often enough to be evaluable and must improve cost or recovery relative to a matched memory-free policy.

v0.15 must therefore pre-register both a performance criterion and a minimum non-vacuous memory-use criterion.
