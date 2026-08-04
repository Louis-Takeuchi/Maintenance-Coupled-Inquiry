# Publication scope decision

## Recommendation

### Publish in the main repository

- Final manuscript and supplement
- Figures and machine-readable tables
- Frozen confirmatory code
- Frozen protocol, pre-run manifest, seed/yoke/chunk plans, and hash audits
- Merged confirmatory run summaries and endpoint analyses
- Execution receipts
- Development and repository-audit reports required to understand design evolution

### Publish v0.14

Yes. Publish v0.14 as a clearly labeled **historical baseline** because it was the audited canonical component baseline and explains how the unified paper-level experiment was reached.

Do not present v0.14 as the code that generated the final paper result.

### Publish v0.1–v0.13

Yes, but only as a compressed provenance archive or separate release asset. They should not occupy the main repository tree because they include superseded designs, exploratory outcomes, and negative-transfer/memory experiments that can confuse the final claim.

### Do not publish by default

- Python bytecode and test caches
- Editor/OS metadata
- Local absolute paths, credentials, API keys, or private notes
- Cover letters, private author contact sheets, reviewer suggestions, or personal submission administration
- Broken or unverifiable ZIP files

## Recommended repository layout

- Main GitHub tree: manuscript, protocol, code, merged data, analysis, figures
- GitHub Release assets: legacy v0.1–v0.14 archive and large reproducibility bundles
- Zenodo/OSF: immutable release ZIP plus checksum, with DOI
