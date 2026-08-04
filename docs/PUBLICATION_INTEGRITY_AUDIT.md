# Publication integrity audit

**Date:** 2026-08-05  
**Result:** `PASS`

## Source preservation

- 315 copied scientific and provenance files were compared with their source
  package counterparts by SHA-256 and matched exactly.
- The comparison covered frozen source, tests, manifests, scripts, protocol,
  figures, manuscript tables and DOCX, supplementary files, merged primary and
  ablation data, final analysis outputs, receipts, development provenance, and
  the expanded v0.14 baseline.
- The manuscript Markdown differs from its source only in the two instructed
  Data Availability and Code Availability paragraphs.
- Confirmatory values, endpoints, SESOIs, decision rules, seed manifest, yoke
  map, protocol, merged data, receipts, and frozen source behavior were not
  modified.

## Executable verification

- Frozen tests: 45/45 passed.
- Public summary checks: passed for 72 confirmatory seeds, 576 primary rows,
  432 ablation rows, 288/288 replay, and all requested headline values.
- Portable processed-analysis reproduction: five tables regenerated using the
  frozen analysis functions, fixed bootstrap seed 941731, and 50,000
  replicates.
- Reproduced/frozen table comparison: 8 + 8 + 8 + 6 + 29 rows matched exactly.
- Relative Markdown link check: 44 links passed at the time of the audit.
- Historical v0.14 manifest: all 73 present listed files matched; 15 stale
  entries referred only to excluded `.pytest_cache`, `__pycache__`, and `.pyc`
  files. The stale manifest was preserved rather than normalized.

## Deliberate non-scientific additions

New English/Japanese README files, claim-boundary documents, portability
helpers, release metadata, license-status notices, security audit, and CI are
publication-layer additions. They do not replace the frozen artifacts.
