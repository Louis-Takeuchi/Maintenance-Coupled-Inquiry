# Confirmatory result summary

The frozen v0.3 verdict supported both the main mechanism claim and the
downstream replicated-restoration claim.

| Result | Value |
|---|---:|
| Primary source runs | 576 |
| Ablation source runs | 432 |
| Exact replay | 288/288 |
| Target sensing difference | +0.1173 |
| Target sensing 95% CI | [+0.0722, +0.1632] |
| Target sensing SESOI | +0.08 |
| Replicated restoration, actual | 41/72 |
| Replicated restoration, yoked | 20/72 |
| Paired restoration difference | +0.2917 |
| Restoration-difference 95% CI | [+0.1667, +0.4167] |
| Neutral actual false repair | 0/72 |
| One-sided 95% upper bound | 0.0408 |

The common decoder reproduced a replicated-restoration advantage of +0.2778
for actual traces over yoked traces, with a 95% CI of [+0.1528, +0.4028]. The
decoder received neither policy identity nor need vectors.

Absolute performance remains limited: actual need achieved replicated
restoration in 41 of 72 self-relevant runs, not all runs. Diagnosis-observation
differences versus yoked need were not clearly separated from zero. The result
supports a scoped functional mechanism, not perfect performance or a claim of
constitutive autonomy.

Canonical machine-readable sources are:

- `data/analysis/v0_3_final_analysis/primary_endpoint_intervals.csv`
- `data/analysis/v0_3_final_analysis/primary_condition_summary.csv`
- `data/analysis/v0_3_final_analysis/common_decoder_diagnostics.csv`
- `data/analysis/v0_3_final_analysis/confirmatory_verdict.csv`
- `data/audits/PaperB_confirmatory_postrun_integrity_audit_v0_3.csv`

