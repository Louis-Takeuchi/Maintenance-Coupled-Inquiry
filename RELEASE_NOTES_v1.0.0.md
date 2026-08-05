# Maintenance-Coupled Inquiry – Public Reproducibility Release v1.0.0

**Tag:** `v1.0.0`  
**Release date:** 2026-08-05  
**Publication state:** Public reproducibility release

## Purpose

This release provides the manuscript, frozen protocol and implementation,
processed confirmatory results, analysis outputs, execution receipts, and
historical context for a preregistered computational experiment on
maintenance-coupled evidence allocation and causal repair.

## Main result and claim boundary

Actual need increased target sensing over yoked need by +0.1173 (95% CI
[+0.0722, +0.1632]; SESOI +0.08). Replicated restoration was 41/72 versus
20/72, a paired difference of +0.2917. Neutral-world false repair was 0/72,
with a one-sided 95% upper bound of 0.0408.

These results support a functional mechanism in the tested microworld. They do
not establish constitutive autonomy, endogenous normativity, biological
individuality, or a general autonomous scientist.

## Included in the Git tree

- Public English and Japanese READMEs
- Manuscript, supplement, figures, and machine-readable tables
- Frozen protocol, source, tests, and manifests
- Merged primary and ablation summaries
- Final endpoint, common-decoder, ablation, verdict, and integrity outputs
- All 120 execution receipts
- Development audit records and expanded historical v0.14 baseline
- Lightweight CI and a verified portable processed-analysis helper

## Excluded from the Git tree

- Large reproducibility ZIPs and cleaned legacy archive (Release assets)
- Full step-level traces (not present in the validated package)
- The earlier broken full-trace ZIP
- Caches, bytecode, OS metadata, local install prompts, and private submission material

## Release asset status and SHA-256

| Asset | Status | SHA-256 |
|---|---|---|
| `PaperB_public_release_all_in_one_2026-08-05_v1_0.zip` | Present and verified | `98be5f2380a74548d3b0cb50e02e28f92b300f46312321973ea9c54d04a00704` |
| corresponding `.sha256` | Present | checksum above |
| `PaperB_legacy_mvp_versions_v0_1_to_v0_14_clean_2026-08-05.zip` | Present and verified | `0d7c4cdcdaa9ecc40ce4d22e141b5622050d996ac2c4a83b3b7cab9f4226b1b2` |
| corresponding legacy `.sha256` | Present | checksum above |

A separate core ZIP is not included. It was not recreated because doing so
would break the byte identity of the previously verified archives.

## Citation and limitations

`CITATION.cff` contains the author in confirmed Unicode form, the repository
URL, version, release date, and Apache-2.0 code license. ORCID, affiliation, and
DOIs are not yet assigned. Figure-generation source and full step-level traces
are also unavailable. The preserved v0.14 checksum list includes 15 stale
cache/bytecode entries; all 73 present listed files verify with the public
helper. See `docs/KNOWN_LIMITATIONS.md` and `docs/REPRODUCIBILITY.md`.
