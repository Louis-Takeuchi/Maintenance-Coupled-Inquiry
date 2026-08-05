# Pre-publication verification for v1.0.0

**Completed:** 2026-08-05 11:55:28 JST  
**Result:** `PASS`

## Scientific and executable verification

- Frozen tests: 45/45 passed.
- Public result audit: passed for 72 confirmatory seeds, 576 primary rows,
  432 ablation rows, 288/288 exact replay, and every published headline value.
- The five selected analysis tables were regenerated with bootstrap seed
  941731 and 50,000 replicates. All 8 + 8 + 8 + 6 + 29 rows matched the frozen
  released tables exactly.
- Scientific result files, frozen code, protocol, manifests, CSV files,
  receipts, tests, figures, and supplementary files changed: 0.
- The English and Japanese manuscript changes are limited to Availability
  statements. The supplementary DOCX is byte-identical to the previous commit.

## Publication-layer verification

- Relative Markdown links: 52 checked, 0 broken.
- CFF YAML: parsed successfully; all 10 required public fields are present.
- Secret patterns: 0 matches.
- Concrete `/Users/` paths outside the audit's literal description: 0.
- `sandbox:/mnt/data` links: 0.
- ChatGPT internal file IDs: 0.
- Tracked `.env`, `.DS_Store`, cache, bytecode, and symlink entries: 0.
- `git diff --check`: passed.

The 127 preserved `/mnt/data/paperB-unified-v1` provenance references described
in `PUBLICATION_SECURITY_AUDIT.md` are not `sandbox:` links or local Mac paths.

## Licenses

The installed texts were byte-compared with the official plain-text license
documents on 2026-08-05:

- `LICENSE` (Apache License 2.0):
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- `LICENSE-DATA` and `LICENSE-DOCS` (CC BY 4.0):
  `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411`

## DOCX rendering

Apple Pages PDF export and PDFKit rendering were used to inspect all pages:

- English manuscript: 32 pages, pass.
- Japanese manuscript: 20 pages, pass.
- Supplementary materials: 7 pages, pass.

No clipping, overlap, missing page, broken heading, missing figure/table, or
missing repository URL was found. Details are in `DOCX_REGENERATION.md`.

## Release asset verification

Both ZIP archives passed compressed-data integrity testing and matched their
sidecar checksum values:

- `PaperB_public_release_all_in_one_2026-08-05_v1_0.zip`:
  `98be5f2380a74548d3b0cb50e02e28f92b300f46312321973ea9c54d04a00704`
- `PaperB_legacy_mvp_versions_v0_1_to_v0_14_clean_2026-08-05.zip`:
  `0d7c4cdcdaa9ecc40ce4d22e141b5622050d996ac2c4a83b3b7cab9f4226b1b2`

The legacy expanded tree verified all 73 present files. Its 15 historical
cache/bytecode checksum entries remain absent by design. A core ZIP was not
recreated.
