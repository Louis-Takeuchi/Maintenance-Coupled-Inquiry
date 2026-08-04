# Public file map

| Public path | Role | Status / source relationship |
|---|---|---|
| `README.md`, `README_ja.md` | Public orientation and claim boundary | New public documents; values checked against frozen CSVs |
| `manuscript/PaperB_AdaptiveBehavior_manuscript_v0_1.md` | Public-link manuscript canonical copy | Source Markdown copied; only Code/Data Availability URLs updated |
| `manuscript/*.docx` | Manuscript DOCX snapshot | Byte-preserved source snapshot; regenerate after Markdown approval |
| `supplement/*.md`, `supplement/*.docx` | Supplementary materials | Byte-preserved source snapshots |
| `manuscript/tables/` | Paper tables | Byte-preserved generated CSVs |
| `figures/` | Released figures | Byte-preserved PDF/PNG; generation script unavailable |
| `protocol/` | Frozen protocol and freeze evidence | Byte-preserved source artifacts |
| `src/` | Canonical confirmatory implementation | Byte-preserved frozen v0.3 source |
| `scripts/*.py` | Frozen runners and analyses | Byte-preserved files moved from the frozen repository root |
| `scripts/archived_postrun/` | Original post-run analysis provenance | Byte-preserved; retains original container paths |
| `scripts/reproduce_processed_analysis.py` | Public portability helper | New, non-frozen wrapper; writes only to a requested output dir |
| `tests/` | Canonical frozen tests | Byte-preserved; 45 tests |
| `manifests/` | Frozen design and execution registries | Byte-preserved; do not edit for reproduction |
| `data/processed/` | Merged confirmatory source summaries | Byte-preserved generated outputs |
| `data/analysis/` | Frozen analysis outputs | Byte-preserved generated outputs |
| `data/execution_receipts/` | Chunk execution provenance | Byte-preserved 120 receipts |
| `docs/development/` | Development and audit history | Selected byte-preserved reports and provenance |
| `legacy/constitutive_inquiry_mvp_v0_14/` | Historical baseline | Byte-preserved expanded v0.14 package |
| all-in-one and core ZIPs | Versioned reproducibility archives | Release assets; not part of Git tree |
| cleaned v0.1–v0.14 ZIP | Development archive | Release asset; not part of Git tree |
| full step-level traces | Raw execution detail | Not included; must be regenerated and separately validated |

The all-in-one package's `MANIFEST.csv` and `SHA256SUMS.txt` describe the
original package layout, not this reorganized Git tree. They remain with the
Release asset and must not be rewritten to imply otherwise.

