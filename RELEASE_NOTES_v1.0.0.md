# Maintenance-Coupled Inquiry – Public Reproducibility Release v1.0.0

**Tag candidate:** `v1.0.0`  
**Release date candidate:** 2026-08-05  
**Publication state:** Draft; do not publish until author and license fields are resolved

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

| Candidate asset | Local status | SHA-256 |
|---|---|---|
| `PaperB_public_release_all_in_one_2026-08-05_v1_0.zip` | Present and verified | `98be5f2380a74548d3b0cb50e02e28f92b300f46312321973ea9c54d04a00704` |
| corresponding `.sha256` | Present | checksum above |
| `PaperB_public_release_core_2026-08-05_v1_0.zip` | Not found; do not create a substitute | — |
| corresponding core `.sha256` | Not found | — |
| `PaperB_legacy_mvp_versions_v0_1_to_v0_14_clean_2026-08-05.zip` | Present and verified | `0d7c4cdcdaa9ecc40ce4d22e141b5622050d996ac2c4a83b3b7cab9f4226b1b2` |
| corresponding legacy `.sha256` | Present | checksum above |

Before publishing, display and recheck the exact tag commit, all uploaded asset
hashes, and the downloaded assets. Do not publish a Release until the license,
author, and citation fields in `PUBLICATION_OPEN_FIELDS.md` are resolved.

## Citation and limitations

`CITATION.cff` is an incomplete draft because author identity, ORCID, DOI, and
license fields are unresolved. Figure-generation source and full step-level
traces are also unavailable. The preserved v0.14 checksum list includes 15
stale cache/bytecode entries; all 73 present listed files verify with the public
helper. See `docs/KNOWN_LIMITATIONS.md` and
`docs/REPRODUCIBILITY.md`.
